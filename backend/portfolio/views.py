import json

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .forms import ContactMessageForm
from .models import Experience, Profile, Project


@never_cache
@require_GET
def contact_token(request):
	return JsonResponse({"csrfToken": get_token(request)})


@require_POST
def contact(request):
	if request.content_type != "application/json":
		return JsonResponse({"error": "Please submit a JSON message."}, status=415)
	if len(request.body) > 32000:
		return JsonResponse({"error": "Your message is too long."}, status=413)
	try:
		data = json.loads(request.body)
	except (ValueError, UnicodeDecodeError):
		return JsonResponse({"error": "The message could not be read."}, status=400)
	if not isinstance(data, dict) or any(
		not isinstance(data.get(key, ""), str) for key in ["name", "email", "message", "website"]
	):
		return JsonResponse({"error": "Please enter valid text in each field."}, status=400)
	if data.get("website", "").strip():
		return JsonResponse({"error": "Unable to accept this submission."}, status=400)
	form = ContactMessageForm(data)
	if not form.is_valid():
		return JsonResponse(
			{
				"error": "Please check the highlighted fields.",
				"errors": {key: list(value) for key, value in form.errors.items()},
			},
			status=400,
		)
	form.save()
	return JsonResponse(
		{"message": "Thanks for reaching out. Your message has been received."}, status=201
	)


@require_GET
def portfolio(request):
	profile = Profile.objects.values().first()
	if profile is None:
		return JsonResponse({"error": "Portfolio content is not configured."}, status=503)
	profile["photo_url"] = (
		settings.MEDIA_URL + profile["photo"] if profile["photo"] else "/santosh-karki.jpg"
	)
	return JsonResponse(
		{
			"profile": profile,
			"projects": list(Project.objects.values()),
			"experience": list(Experience.objects.values()),
		}
	)


@require_GET
def resume(request):
	return FileResponse(
		(settings.BASE_DIR / "assets" / "Santosh_Kumar_Karki_CV.pdf").open("rb"),
		as_attachment=True,
		filename="Santosh_Kumar_Karki_CV.pdf",
		content_type="application/pdf",
	)
