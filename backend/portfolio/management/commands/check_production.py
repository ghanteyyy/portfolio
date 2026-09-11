from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = "Reject development settings and weak administrator accounts before serving production."

	def handle(self, *args, **options):
		if settings.DEBUG:
			raise CommandError("Production requires DJANGO_DEBUG=false.")
		for user in get_user_model().objects.filter(is_staff=True, is_active=True):
			if user.check_password("admin"):
				raise CommandError(
					"An active administrator still uses the demo password. Change it before deployment."
				)
		self.stdout.write(self.style.SUCCESS("Production account checks passed."))
