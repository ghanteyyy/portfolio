import json
import re
from functools import wraps
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.forms import modelform_factory
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import ContactMessage, Experience, Profile, Project

MODELS = {
	"projects": (Project, ["title", "category", "description", "tags", "url", "order"]),
	"experience": (
		Experience,
		["role", "organization", "location", "period", "description", "order"],
	),
	"profile": (
		Profile,
		[
			"name",
			"role",
			"summary",
			"email",
			"phone",
			"location",
			"github",
			"linkedin",
			"skills",
			"education",
		],
	),
	"messages": (ContactMessage, ["is_read"]),
}


@require_http_methods(["GET"])
def portrait(request, filename):
	if not re.fullmatch(r"[0-9a-f]{32}\.jpg", filename):
		raise Http404
	path = settings.MEDIA_ROOT / "portraits" / filename
	try:
		response = FileResponse(path.open("rb"), content_type="image/jpeg")
	except FileNotFoundError:
		raise Http404
	response["X-Content-Type-Options"] = "nosniff"
	response["Cache-Control"] = "public, max-age=86400"
	return response


def permissions(user, model):
	prefix = f"{model._meta.app_label}."
	return {
		action: user.has_perm(f"{prefix}{action}_{model._meta.model_name}")
		for action in ["view", "add", "change", "delete"]
	}


def staff_only(view):
	@wraps(view)
	@never_cache
	def wrapped(request, *args, **kwargs):
		if not request.user.is_authenticated:
			return JsonResponse({"error": "Please sign in."}, status=401)
		if not request.user.is_active or not request.user.is_staff:
			return JsonResponse({"error": "Admin access is required."}, status=403)
		return view(request, *args, **kwargs)

	return wrapped


def payload(request):
	if request.content_type != "application/json" or len(request.body) > 100000:
		raise ValueError("Invalid request.")
	data = json.loads(request.body)
	if not isinstance(data, dict):
		raise ValueError("Expected an object.")
	return data


@never_cache
@require_http_methods(["GET", "POST", "DELETE"])
def session(request):
	if request.method == "DELETE":
		logout(request)
		return JsonResponse({"ok": True})
	if request.method == "POST":
		try:
			data = payload(request)
		except (ValueError, UnicodeDecodeError):
			return JsonResponse({"error": "Enter your email and password."}, status=400)
		email, password = data.get("email"), data.get("password")
		if (
			not isinstance(email, str)
			or not isinstance(password, str)
			or len(email) > 254
			or len(password) > 1024
		):
			return JsonResponse({"error": "Enter your email and password."}, status=400)
		user = authenticate(request, username=email, password=password)
		if user is None or not user.is_staff:
			return JsonResponse(
				{
					"error": "Incorrect email or password, or this account does not have admin access."
				},
				status=400,
			)
		login(request, user)
	if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
		return JsonResponse({"error": "Please sign in with an admin account."}, status=401)
	return JsonResponse(
		{
			"user": {
				"name": request.user.get_short_name() or request.user.email,
				"email": request.user.email,
			},
			"permissions": {
				key: permissions(request.user, model) for key, (model, _) in MODELS.items()
			},
		}
	)


@staff_only
@require_http_methods(["GET", "POST", "PATCH", "DELETE"])
def records(request, resource, pk=None):
	if resource not in MODELS:
		return JsonResponse({"error": "Not found."}, status=404)
	model, fields = MODELS[resource]
	allowed = permissions(request.user, model)
	action = {"GET": "view", "POST": "add", "PATCH": "change", "DELETE": "delete"}[request.method]
	if not (allowed[action] or (action == "view" and allowed["change"])):
		return JsonResponse({"error": "You do not have permission for this action."}, status=403)
	if request.method == "GET":
		return JsonResponse({"records": list(model.objects.values())})
	if request.method == "POST" and (pk is not None or resource == "messages"):
		return JsonResponse({"error": "This action is not available."}, status=405)
	instance = None
	if request.method in ["PATCH", "DELETE"]:
		instance = model.objects.filter(pk=pk).first()
		if instance is None:
			return JsonResponse({"error": "Record not found."}, status=404)
	if request.method == "DELETE":
		instance.delete()
		return JsonResponse({"ok": True})
	try:
		data = payload(request)
	except (ValueError, UnicodeDecodeError):
		return JsonResponse({"error": "Unable to read your changes."}, status=400)
	if resource == "messages" and (
		set(data) != {"is_read"} or not isinstance(data["is_read"], bool)
	):
		return JsonResponse({"error": "Only the read status can be updated."}, status=400)
	if instance:
		data = {**{field: getattr(instance, field) for field in fields}, **data}
	for field in ["tags", "skills", "education"]:
		if field in data and not isinstance(data[field], str):
			data[field] = json.dumps(data[field])
	form = modelform_factory(model, fields=fields)(data, instance=instance)
	if not form.is_valid():
		return JsonResponse(
			{
				"error": "Please correct the highlighted fields.",
				"errors": {key: list(value) for key, value in form.errors.items()},
			},
			status=400,
		)
	cleaned = form.cleaned_data
	if resource == "projects" and (
		not isinstance(cleaned["tags"], list)
		or not all(isinstance(tag, str) for tag in cleaned["tags"])
	):
		return JsonResponse(
			{
				"error": "Tags must be a list of text values.",
				"errors": {"tags": ["Use a JSON list of strings."]},
			},
			status=400,
		)
	if resource == "profile":
		skills = cleaned["skills"]
		valid_skills = isinstance(skills, list) and all(
			isinstance(group, dict)
			and isinstance(group.get("label"), str)
			and isinstance(group.get("icon"), str)
			and isinstance(group.get("items"), list)
			and all(isinstance(item, str) for item in group["items"])
			for group in skills
		)
		education = cleaned["education"]
		if (
			not valid_skills
			or not isinstance(education, dict)
			or not all(
				isinstance(education.get(key), str)
				for key in ["degree", "short", "institution", "period"]
			)
		):
			return JsonResponse(
				{"error": "Keep the existing skills and education structure."}, status=400
			)
	record = form.save()
	return JsonResponse(
		{"record": model.objects.filter(pk=record.pk).values().get()},
		status=201 if request.method == "POST" else 200,
	)


@staff_only
@require_http_methods(["POST"])
def upload_photo(request, pk):
	if not request.user.has_perm("portfolio.change_profile"):
		return JsonResponse(
			{"error": "You do not have permission to change the photo."}, status=403
		)
	profile = Profile.objects.filter(pk=pk).first()
	if profile is None:
		return JsonResponse({"error": "Profile not found."}, status=404)
	upload = request.FILES.get("photo")
	if upload is None:
		return JsonResponse({"error": "Choose a photo to upload."}, status=400)
	if upload.size > 5 * 1024 * 1024:
		return JsonResponse({"error": "Choose an image smaller than 5 MB."}, status=400)
	try:
		with Image.open(upload) as original:
			if original.format not in {"JPEG", "PNG", "WEBP"}:
				raise ValueError("Choose a JPEG, PNG, or WebP image.")
			if original.width * original.height > 16000000:
				raise ValueError("Choose an image with no more than 16 million pixels.")
			original.load()
			picture = ImageOps.exif_transpose(original).convert("RGBA")
			picture.thumbnail((1200, 1200))
			background = Image.new("RGB", picture.size, "white")
			background.paste(picture, mask=picture.getchannel("A"))
			result = BytesIO()
			background.save(result, format="JPEG", quality=90)
	except ValueError as error:
		return JsonResponse({"error": str(error)}, status=400)
	except (
		UnidentifiedImageError,
		OSError,
		Image.DecompressionBombError,
		Image.DecompressionBombWarning,
	):
		return JsonResponse(
			{"error": "This image could not be read. Choose a valid JPEG, PNG, or WebP."},
			status=400,
		)
	profile.photo.save(f"{uuid4().hex}.jpg", ContentFile(result.getvalue()), save=True)
	return JsonResponse({"photo": profile.photo.name, "photo_url": profile.photo.url})
