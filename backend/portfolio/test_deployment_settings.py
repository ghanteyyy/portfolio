import os
from importlib.util import find_spec
from pathlib import Path
from unittest.mock import patch

from config.production import database_from_url
from django.test import SimpleTestCase


class DeploymentSettingsTests(SimpleTestCase):
	def settings(self, **overrides):
		environment = {
			"RENDER": "true",
			"DJANGO_DEBUG": "false",
			"DJANGO_SECRET_KEY": "test-only-abcdefghijklmnopqrstuvwxyz-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
			"RENDER_EXTERNAL_HOSTNAME": "portfolio.onrender.com",
			"DATABASE_URL": "postgresql://user:p%40ss@db.example/portfolio?sslmode=require&channel_binding=require",
			"REDIS_URL": "rediss://cache.example:6379/0",
			**overrides,
		}
		with patch.dict(os.environ, environment, clear=True), patch("dotenv.load_dotenv"):
			namespace = {"__file__": find_spec("config.settings").origin, "__package__": "config"}
			exec(
				compile(Path(namespace["__file__"]).read_text(), namespace["__file__"], "exec"),
				namespace,
			)
			return namespace

	def test_render_uses_postgres_and_https(self):
		settings = self.settings()
		database = settings["DATABASES"]["default"]
		self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
		self.assertEqual(database["PASSWORD"], "p@ss")
		self.assertEqual(database["OPTIONS"]["channel_binding"], "require")
		self.assertIn("portfolio.onrender.com", settings["ALLOWED_HOSTS"])
		self.assertIn("https://portfolio.onrender.com", settings["CSRF_TRUSTED_ORIGINS"])
		self.assertTrue(settings["SESSION_COOKIE_SECURE"])
		self.assertTrue(settings["TRUST_PROXY_HEADERS"])

	def test_render_rejects_debug_and_missing_database(self):
		with self.assertRaisesRegex(RuntimeError, "DJANGO_DEBUG=false"):
			self.settings(DJANGO_DEBUG="true")
		with self.assertRaisesRegex(RuntimeError, "Set DATABASE_URL"):
			self.settings(DATABASE_URL="")

	def test_invalid_url_does_not_expose_credentials(self):
		for url in ["sqlite:///tmp/db.sqlite3", "postgresql://user:secret@host:bad/db"]:
			with self.assertRaises(RuntimeError) as raised:
				database_from_url(url)
			self.assertNotIn("secret", str(raised.exception))

	def test_local_sqlite_is_preserved(self):
		settings = self.settings(RENDER="false", DJANGO_DEBUG="true", DATABASE_URL="")
		self.assertEqual(settings["DATABASES"]["default"]["ENGINE"], "django.db.backends.sqlite3")

	def test_production_can_start_without_redis(self):
		settings = self.settings(REDIS_URL="")
		self.assertFalse(settings["DEBUG"])
		self.assertFalse(settings["REDIS_URL"])
		self.assertTrue(settings["RATE_LIMIT_ENABLED"])
