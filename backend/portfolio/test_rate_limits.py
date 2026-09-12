from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase, override_settings, skipUnlessDBFeature
from django.utils import timezone

from .models import RateLimitBucket
from .rate_limits import increment_database_limit


@override_settings(REDIS_URL="", RATE_LIMIT_ENABLED=True)
class DatabaseRateLimitTests(TestCase):
	def test_enforcement_without_redis(self):
		for _ in range(5):
			self.assertEqual(
				self.client.post("/api/contact/", {}, content_type="application/json").status_code,
				400,
			)
		self.assertEqual(
			self.client.post("/api/contact/", {}, content_type="application/json").status_code, 429
		)
		self.assertEqual(RateLimitBucket.objects.get().count, 6)

	def test_expired_limit_resets_and_old_rows_are_pruned(self):
		past = timezone.now() - timedelta(seconds=1)
		RateLimitBucket.objects.create(key="current", count=99, expires_at=past)
		RateLimitBucket.objects.create(key="old", count=99, expires_at=past)
		self.assertEqual(increment_database_limit("current", 300), 1)
		self.assertFalse(RateLimitBucket.objects.filter(pk="old").exists())
		self.assertEqual(increment_database_limit("current", 300), 2)


class ConcurrentRateLimitTests(TransactionTestCase):
	@skipUnlessDBFeature("has_select_for_update")
	def test_concurrent_requests_keep_all_increments(self):
		def increment(_):
			close_old_connections()
			try:
				return increment_database_limit("shared", 300)
			finally:
				close_old_connections()

		with ThreadPoolExecutor(max_workers=4) as pool:
			counts = list(pool.map(increment, range(8)))
		self.assertEqual(sorted(counts), list(range(1, 9)))
