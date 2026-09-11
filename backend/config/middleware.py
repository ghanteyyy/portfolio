import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ProductionMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if settings.RATE_LIMIT_ENABLED and request.method == "POST":
			limit = None
			if request.path == "/api/studio/session/":
				limit = (10, 300)
			elif request.path == "/api/contact/":
				limit = (5, 3600)
			elif request.path.endswith("/photo/"):
				limit = (20, 3600)
			if limit:
				address = request.META.get("REMOTE_ADDR", "unknown")
				if settings.TRUST_PROXY_HEADERS:
					address = (
						request.META.get("HTTP_X_FORWARDED_FOR", address).split(",")[0].strip()
					)
				key = "rate:" + hashlib.sha256(f"{request.path}:{address}".encode()).hexdigest()
				try:
					if cache.add(key, 1, timeout=limit[1]):
						count = 1
					else:
						try:
							count = cache.incr(key)
						except ValueError:
							cache.add(key, 1, timeout=limit[1])
							count = 1
				except Exception:
					logger.exception("Rate limit storage is unavailable")
					return JsonResponse(
						{"error": "Temporarily unavailable. Please try again later."}, status=503
					)
				if count > limit[0]:
					response = JsonResponse(
						{"error": "Too many attempts. Please try again later."}, status=429
					)
					response["Retry-After"] = str(limit[1])
					return response
		response = self.get_response(request)
		if not settings.DEBUG:
			response["Content-Security-Policy"] = (
				"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
				"font-src 'self' https://fonts.gstatic.com; img-src 'self' blob: data:; connect-src 'self'; "
				"object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
			)
			response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
		return response

	def process_exception(self, request, exception):
		if isinstance(exception, RequestDataTooBig):
			return JsonResponse({"error": "This request is too large."}, status=413)
		return None


def csrf_failure(request, reason=""):
	return JsonResponse(
		{"error": "Your session could not be verified. Refresh the page and try again."}, status=403
	)
