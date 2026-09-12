# Deployment

Requires a Linux server, Docker Compose, a domain pointing to the server, and open ports 80/443. The stack includes HTTPS via Caddy, Gunicorn, PostgreSQL, and Redis.

## Setup

Copy `.env.production.example` to `.env.production`. Set your domain, certificate email, and separate strong secrets for Django and PostgreSQL. Generate each secret with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

Run from the project root:

```sh
docker compose --env-file .env.production up -d --build
docker compose --env-file .env.production exec web python manage.py seed_portfolio
docker compose --env-file .env.production exec web python manage.py createsuperuser
```

Visit `https://YOUR_DOMAIN/admin/`. Use a strong password; the demo password `admin` blocks production startup. Existing local content and uploads must be transferred separately.

## Verify and maintain

```sh
docker compose --env-file .env.production ps
curl --fail https://YOUR_DOMAIN/api/health/
docker compose --env-file .env.production logs --tail 100 web caddy
```

Back up PostgreSQL and the media volume before updates. Re-run `up -d --build` to deploy changes. Keep secrets private and never use `down -v` unless you intend to delete stored data.

## Render

`render.yaml` configures a free Docker web service using your existing Neon PostgreSQL database. Redis is optional: without `REDIS_URL`, rate limits use PostgreSQL.

1. Push the updated code, including migrations. Keep `.env.production` and `.env.render` private.
2. For an existing service, import `.env.render` under **Environment â†’ Add from .env**. Remove any unused or invalid `REDIS_URL`, then redeploy.
3. Alternatively, create a Blueprint from `render.yaml` and enter the secret and database URL when prompted. Match its service name to your existing service before applying it.
4. Add your domain under **Settings â†’ Custom Domains** and apply Render's DNS records. Set the health check to `/api/health/`.

Startup applies migrations and seeds CV content only when no profile exists. Create a strong administrator after deployment. Free Render uploads are temporary; persistent admin photos still require external image storage.
