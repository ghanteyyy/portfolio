from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from .models import ContactMessage, Profile, Project


@override_settings(RATE_LIMIT_ENABLED=False)
class PortfolioTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		call_command("seed_portfolio", verbosity=0)

	def test_cv_content_is_available(self):
		response = self.client.get("/api/portfolio/")
		self.assertEqual(response.status_code, 200)
		content = response.json()
		self.assertEqual(content["profile"]["name"], "Santosh Kumar Karki")
		self.assertEqual(len(content["projects"]), 5)
		self.assertEqual(len(content["experience"]), 2)
		self.assertEqual(
			content["projects"][2]["url"], "https://github.com/ghanteyyy/django_prod_strater"
		)

	def test_admin_edits_appear_in_api_and_seeding_preserves_them(self):
		profile = Profile.objects.get(pk=1)
		profile.summary = "Updated through the admin."
		profile.save()
		call_command("seed_portfolio", verbosity=0)
		self.assertEqual(
			self.client.get("/api/portfolio/").json()["profile"]["summary"], profile.summary
		)
		self.assertEqual(Project.objects.count(), 5)

	def test_public_api_cannot_modify_content(self):
		self.assertEqual(self.client.post("/api/portfolio/", {"name": "changed"}).status_code, 405)

	def test_resume_download_is_a_pdf(self):
		response = self.client.get("/resume/")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "application/pdf")
		self.assertIn("attachment", response["Content-Disposition"])
		self.assertTrue(b"".join(response.streaming_content).startswith(b"%PDF"))

	def test_admin_requires_login(self):
		response = self.client.get("/api/studio/session/")
		self.assertEqual(response.status_code, 401)

	def test_missing_profile_is_reported(self):
		Profile.objects.all().delete()
		self.assertEqual(self.client.get("/api/portfolio/").status_code, 503)


@override_settings(RATE_LIMIT_ENABLED=False)
class ContactTests(TestCase):
	def setUp(self):
		self.client = Client(enforce_csrf_checks=True)
		self.token = self.client.get("/api/contact/token/").json()["csrfToken"]
		self.payload = {
			"name": "A Visitor",
			"email": "visitor@example.com",
			"message": "I would like to discuss a project.",
			"website": "",
		}

	def submit(self, data=None, **kwargs):
		return self.client.post(
			"/api/contact/",
			data=self.payload if data is None else data,
			content_type="application/json",
			HTTP_X_CSRFTOKEN=self.token,
			**kwargs,
		)

	def test_submission_saves_private_message(self):
		response = self.submit(HTTP_ORIGIN="http://testserver")
		self.assertEqual(response.status_code, 201)
		message = ContactMessage.objects.get()
		self.assertEqual(message.email, self.payload["email"])
		self.assertEqual(message.message, self.payload["message"])
		self.assertFalse(message.is_read)
		self.assertEqual(self.client.get("/api/contact/").status_code, 405)
		self.assertEqual(self.client.get("/api/studio/messages/").status_code, 401)

	def test_csrf_and_untrusted_origin_are_rejected(self):
		self.assertEqual(
			self.client.post(
				"/api/contact/", self.payload, content_type="application/json"
			).status_code,
			403,
		)
		self.assertEqual(self.submit(HTTP_ORIGIN="https://untrusted.example").status_code, 403)
		self.assertEqual(ContactMessage.objects.count(), 0)

	def test_invalid_fields_are_not_saved(self):
		for field, value in [
			("name", "   "),
			("email", "invalid"),
			("message", ""),
			("message", "x" * 5001),
		]:
			with self.subTest(field=field, length=len(value)):
				response = self.submit({**self.payload, field: value})
				self.assertEqual(response.status_code, 400)
				self.assertIn(field, response.json()["errors"])
		self.assertEqual(ContactMessage.objects.count(), 0)

	def test_malformed_payloads_and_honeypot_are_rejected(self):
		for data in ["{broken", [], {"name": []}, {**self.payload, "website": "spam.example"}]:
			with self.subTest(data=data):
				self.assertEqual(self.submit(data).status_code, 400)
		self.assertEqual(ContactMessage.objects.count(), 0)


@override_settings(RATE_LIMIT_ENABLED=False)
class ReactStudioTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_superuser(
			"react-owner", "owner@example.com", "test-password"
		)
		self.client = Client(enforce_csrf_checks=True)

	def request(self, path, method="post", data=None):
		token = self.client.get("/api/contact/token/").json()["csrfToken"]
		return getattr(self.client, method)(
			path, data=data or {}, content_type="application/json", HTTP_X_CSRFTOKEN=token
		)

	def sign_in(self):
		response = self.request(
			"/api/studio/session/", data={"email": "OWNER@example.com", "password": "test-password"}
		)
		self.assertEqual(response.status_code, 200)

	def test_session_and_csrf(self):
		self.assertEqual(self.client.get("/api/studio/projects/").status_code, 401)
		self.assertEqual(
			self.client.post(
				"/api/studio/session/",
				{"email": "owner@example.com"},
				content_type="application/json",
			).status_code,
			403,
		)
		self.assertEqual(
			self.request(
				"/api/studio/session/", data={"email": "owner@example.com", "password": "wrong"}
			).status_code,
			400,
		)
		self.sign_in()
		self.assertEqual(
			self.client.get("/api/studio/session/").json()["user"]["email"], "owner@example.com"
		)
		self.assertEqual(self.request("/api/studio/session/", "delete").status_code, 200)
		self.assertEqual(self.client.get("/api/studio/projects/").status_code, 401)

	def test_project_crud_and_validation(self):
		self.sign_in()
		data = {
			"title": "React project",
			"category": "API",
			"description": "A test project",
			"tags": ["Django"],
			"url": "https://example.com/project",
			"order": 1,
		}
		response = self.request("/api/studio/projects/", data=data)
		self.assertEqual(response.status_code, 201)
		pk = response.json()["record"]["id"]
		url = f"/api/studio/projects/{pk}/"
		self.assertEqual(self.request(url, "patch", {"title": "Updated"}).status_code, 200)
		self.assertEqual(Project.objects.get(pk=pk).title, "Updated")
		self.assertEqual(self.request(url, "patch", {"tags": {"bad": "shape"}}).status_code, 400)
		self.assertEqual(self.request(url, "delete").status_code, 200)
		self.assertFalse(Project.objects.filter(pk=pk).exists())

	def test_permissions_and_message_integrity(self):
		message = ContactMessage.objects.create(
			name="Visitor", email="v@example.com", message="Private"
		)
		self.sign_in()
		url = f"/api/studio/messages/{message.pk}/"
		self.assertEqual(self.request(url, "patch", {"is_read": True}).status_code, 200)
		self.assertEqual(self.request(url, "patch", {"message": "Changed"}).status_code, 400)
		self.user.is_superuser = False
		self.user.save()
		self.assertEqual(self.client.get("/api/studio/messages/").status_code, 403)


@override_settings(RATE_LIMIT_ENABLED=False)
class ProfilePhotoTests(TestCase):
	def setUp(self):
		import tempfile

		from django.test import override_settings

		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		from pathlib import Path

		override = override_settings(MEDIA_ROOT=Path(self.temp.name))
		override.enable()
		self.addCleanup(override.disable)
		call_command("seed_portfolio", verbosity=0)
		self.user = get_user_model().objects.create_superuser(
			"photo-owner", "photo@example.com", "test-password"
		)
		self.client = Client(enforce_csrf_checks=True)
		self.client.force_login(self.user)
		self.token = self.client.get("/api/contact/token/").json()["csrfToken"]

	def image(self):
		from io import BytesIO

		from django.core.files.uploadedfile import SimpleUploadedFile
		from PIL import Image

		stream = BytesIO()
		Image.new("RGB", (100, 100), "blue").save(stream, "PNG")
		return SimpleUploadedFile("portrait.png", stream.getvalue(), content_type="image/png")

	def test_upload_updates_public_portrait(self):
		response = self.client.post(
			"/api/studio/profile/1/photo/", {"photo": self.image()}, HTTP_X_CSRFTOKEN=self.token
		)
		self.assertEqual(response.status_code, 200)
		photo_url = response.json()["photo_url"]
		self.assertEqual(
			self.client.get("/api/portfolio/").json()["profile"]["photo_url"], photo_url
		)
		self.client.logout()
		response = self.client.get(photo_url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "image/jpeg")
		response.close()

	def test_invalid_image_and_csrf(self):
		from django.core.files.uploadedfile import SimpleUploadedFile

		response = self.client.post("/api/studio/profile/1/photo/", {"photo": self.image()})
		self.assertEqual(response.status_code, 403)
		fake = SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")
		response = self.client.post(
			"/api/studio/profile/1/photo/", {"photo": fake}, HTTP_X_CSRFTOKEN=self.token
		)
		self.assertEqual(response.status_code, 400)
		self.assertFalse(Profile.objects.get(pk=1).photo)

	def test_upload_requires_profile_change_permission(self):
		self.user.is_superuser = False
		self.user.save()
		response = self.client.post(
			"/api/studio/profile/1/photo/", {"photo": self.image()}, HTTP_X_CSRFTOKEN=self.token
		)
		self.assertEqual(response.status_code, 403)

	def test_oversized_file_rejected(self):
		from django.core.files.uploadedfile import SimpleUploadedFile

		image = SimpleUploadedFile(
			"large.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
		)
		response = self.client.post(
			"/api/studio/profile/1/photo/", {"photo": image}, HTTP_X_CSRFTOKEN=self.token
		)
		self.assertEqual(response.status_code, 400)
		self.assertFalse(Profile.objects.get(pk=1).photo)


@override_settings(RATE_LIMIT_ENABLED=False)
class ReactOnlyAdminRoutesTests(TestCase):
	def test_legacy_interface_is_unavailable(self):
		self.assertEqual(self.client.get("/django-admin/").status_code, 404)
		self.assertEqual(self.client.get("/django-admin/login/").status_code, 404)

	def test_react_entrypoints_remain_available(self):
		for route in ["/admin/", "/login/"]:
			response = self.client.get(route)
			self.assertEqual(response.status_code, 200)
			self.assertTemplateUsed(response, "index.html")
			self.assertContains(response, '<div id="root"></div>')
		self.assertRedirects(self.client.get("/admin/login/"), "/login/")
