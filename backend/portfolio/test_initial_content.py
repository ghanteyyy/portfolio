from django.core.management import call_command
from django.test import TestCase

from .models import Profile, Project


class InitialContentTests(TestCase):
	def test_empty_database_is_ready_after_startup_seed(self):
		call_command("seed_portfolio", if_empty=True)
		self.assertEqual(self.client.get("/api/portfolio/").status_code, 200)
		self.assertTrue(Project.objects.exists())

	def test_repeat_startup_preserves_edits_and_deletions(self):
		call_command("seed_portfolio", if_empty=True)
		profile = Profile.objects.first()
		profile.summary = "My edited summary"
		profile.save()
		Project.objects.all().delete()
		call_command("seed_portfolio", if_empty=True)
		profile.refresh_from_db()
		self.assertEqual(profile.summary, "My edited summary")
		self.assertFalse(Project.objects.exists())
