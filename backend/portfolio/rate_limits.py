from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import RateLimitBucket


def increment_database_limit(key, seconds):
	"""Serialize counters across PostgreSQL workers without a Redis dependency."""
	now = timezone.now()
	# Prune expired rows before acquiring the current bucket's row lock.
	RateLimitBucket.objects.filter(expires_at__lte=now).exclude(pk=key).delete()
	with transaction.atomic():
		bucket, _ = RateLimitBucket.objects.select_for_update().get_or_create(
			key=key, defaults={"expires_at": now + timedelta(seconds=seconds)}
		)
		if bucket.expires_at <= now:
			bucket.count = 0
			bucket.expires_at = now + timedelta(seconds=seconds)
		bucket.count += 1
		bucket.save(update_fields=["count", "expires_at"])
		return bucket.count
