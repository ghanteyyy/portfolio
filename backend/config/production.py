"""Environment configuration shared by local and container deployments."""

import os


def env_bool(name, default=False):
	return os.getenv(name, str(default)).lower() in {"1", "true", "yes"}


def env_list(name, default=""):
	return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


def database_from_url(url):
	from psycopg.conninfo import conninfo_to_dict

	try:
		if not url.startswith(("postgres://", "postgresql://")):
			raise ValueError
		values = conninfo_to_dict(url)
		if "port" in values and not 1 <= int(values["port"]) <= 65535:
			raise ValueError
		if not values.get("host") or not values.get("dbname"):
			raise ValueError
	except Exception:
		raise RuntimeError(
			"DATABASE_URL must be a valid PostgreSQL connection URL with a host and database name."
		) from None
	fields = {
		"dbname": "NAME",
		"user": "USER",
		"password": "PASSWORD",
		"host": "HOST",
		"port": "PORT",
	}
	database = {
		"ENGINE": "django.db.backends.postgresql",
		"CONN_MAX_AGE": 60,
		"CONN_HEALTH_CHECKS": True,
	}
	for key, field in fields.items():
		if key in values:
			database[field] = values.pop(key)
	database["OPTIONS"] = {"connect_timeout": 5, "sslmode": "require", **values}
	return database
