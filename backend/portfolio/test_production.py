from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings


@override_settings(RATE_LIMIT_ENABLED=True, TRUST_PROXY_HEADERS=False)
class ProductionTests(TestCase):
	def setUp(self):
		cache.clear()

	def test_login_limit_ignores_spoofed_forwarded_addresses(self):
		for index in range(10):
			response = self.client.post(
				"/api/studio/session/",
				{},
				content_type="application/json",
				HTTP_X_FORWARDED_FOR=f"10.0.0.{index}",
			)
			self.assertEqual(response.status_code, 400)
		response = self.client.post("/api/studio/session/", {}, content_type="application/json")
		self.assertEqual(response.status_code, 429)
		self.assertEqual(response["Retry-After"], "300")

	def test_contact_limit_and_separate_clients(self):
		for _ in range(5):
			self.assertEqual(
				self.client.post("/api/contact/", {}, content_type="application/json").status_code,
				400,
			)
		self.assertEqual(
			self.client.post("/api/contact/", {}, content_type="application/json").status_code, 429
		)
		self.assertEqual(
			self.client.post(
				"/api/contact/", {}, content_type="application/json", REMOTE_ADDR="192.0.2.2"
			).status_code,
			400,
		)

	def test_health(self):
		self.assertEqual(self.client.get("/api/health/").json(), {"status": "ok"})
		with patch(
			"config.health.cache.get", side_effect=ConnectionError("private connection details")
		):
			response = self.client.get("/api/health/")
		self.assertEqual(response.status_code, 503)
		self.assertEqual(response.json(), {"status": "unavailable"})

	def test_cache_failure_does_not_allow_unlimited_attempts(self):
		with patch("config.middleware.cache.add", side_effect=ConnectionError("offline")):
			response = self.client.post("/api/contact/", {}, content_type="application/json")
		self.assertEqual(response.status_code, 503)

	@override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False)
	def test_security_headers(self):
		response = self.client.get("/api/health/")
		self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
		self.assertEqual(response["X-Content-Type-Options"], "nosniff")

	@override_settings(DEBUG=False)
	def test_demo_password_blocks_production(self):
		user = get_user_model().objects.create_user(
			username="admin", email="admin@admin.com", password="admin", is_staff=True
		)
		with self.assertRaises(CommandError):
			call_command("check_production")
		user.set_password("a-new-strong-password-for-this-test")
		user.save()
		call_command("check_production")
