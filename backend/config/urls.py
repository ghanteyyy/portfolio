from django.urls import path
from django.views.generic import RedirectView, TemplateView
from portfolio import studio_api
from portfolio.views import contact, contact_token, portfolio, resume

from config.health import health

urlpatterns = [
	path("api/health/", health),
	path("login/", TemplateView.as_view(template_name="index.html"), name="studio_login"),
	path(
		"admin/login/",
		RedirectView.as_view(pattern_name="studio_login", query_string=True, permanent=False),
	),
	path("admin/", TemplateView.as_view(template_name="index.html")),
	path("media/portraits/<str:filename>", studio_api.portrait),
	path("api/studio/profile/<int:pk>/photo/", studio_api.upload_photo),
	path("api/studio/session/", studio_api.session),
	path("api/studio/<str:resource>/", studio_api.records),
	path("api/studio/<str:resource>/<int:pk>/", studio_api.records),
	path("api/portfolio/", portfolio),
	path("api/contact/token/", contact_token),
	path("api/contact/", contact),
	path("resume/", resume),
	path("", TemplateView.as_view(template_name="index.html")),
]
