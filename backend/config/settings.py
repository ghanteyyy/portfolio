import os
from pathlib import Path

from dotenv import load_dotenv

from .production import database_from_url, env_bool, env_list

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env", override=False)
DEBUG = env_bool("DJANGO_DEBUG")
ON_RENDER = env_bool("RENDER")
if ON_RENDER and DEBUG:
	raise RuntimeError(
		"Set DJANGO_DEBUG=false on Render and configure DATABASE_URL for PostgreSQL."
	)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1" if DEBUG else "")
if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
	ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
if not SECRET_KEY or (not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith("replace-"))):
	raise RuntimeError("Set a strong DJANGO_SECRET_KEY (at least 50 characters in production).")
if not DEBUG and (not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS):
	raise RuntimeError("Set explicit DJANGO_ALLOWED_HOSTS for production.")
INSTALLED_APPS = [
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"portfolio",
]
MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"config.middleware.ProductionMiddleware",
	"whitenoise.middleware.WhiteNoiseMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR.parent / "frontend" / "dist"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			]
		},
	}
]
WSGI_APPLICATION = "config.wsgi.application"
if os.getenv("DATABASE_URL"):
	DATABASES = {"default": database_from_url(os.environ["DATABASE_URL"])}
elif os.getenv("POSTGRES_HOST"):
	DATABASES = {
		"default": {
			"ENGINE": "django.db.backends.postgresql",
			"NAME": os.environ["POSTGRES_DB"],
			"USER": os.environ["POSTGRES_USER"],
			"PASSWORD": os.environ["POSTGRES_PASSWORD"],
			"HOST": os.environ["POSTGRES_HOST"],
			"PORT": os.getenv("POSTGRES_PORT", "5432"),
			"CONN_MAX_AGE": 60,
			"CONN_HEALTH_CHECKS": True,
			"OPTIONS": {"connect_timeout": 5, "sslmode": os.getenv("POSTGRES_SSLMODE", "prefer")},
		}
	}
elif DEBUG:
	DATABASES = {
		"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
	}
else:
	raise RuntimeError(
		"Set DATABASE_URL or POSTGRES_HOST/DB/USER/PASSWORD to configure PostgreSQL for production."
	)
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
	CACHES = {
		"default": {
			"BACKEND": "django.core.cache.backends.redis.RedisCache",
			"LOCATION": REDIS_URL,
			"OPTIONS": {"socket_connect_timeout": 3, "socket_timeout": 3},
		}
	}

RATE_LIMIT_ENABLED = env_bool("RATE_LIMIT_ENABLED", True)
AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_ROOT = BASE_DIR.parent / "frontend" / "dist"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
AUTHENTICATION_BACKENDS = ["config.auth.EmailBackend"]
CSRF_TRUSTED_ORIGINS = env_list(
	"CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173" if DEBUG else ""
)

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/admin/"

if ON_RENDER and os.getenv("RENDER_EXTERNAL_HOSTNAME"):
	CSRF_TRUSTED_ORIGINS.append("https://" + os.environ["RENDER_EXTERNAL_HOSTNAME"])
TRUST_PROXY_HEADERS = env_bool("TRUST_PROXY_HEADERS", ON_RENDER)
if TRUST_PROXY_HEADERS:
	SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("HSTS_PRELOAD", False)
# Subdomains and browser preload require a separate domain-wide HTTPS decision.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 28800
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_FAILURE_VIEW = "config.middleware.csrf_failure"
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 1
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50
LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {"standard": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
	"handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"}},
	"root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
	"loggers": {"django.server": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}
