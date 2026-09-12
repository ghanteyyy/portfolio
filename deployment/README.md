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

`render.yaml` configures a free Docker web service and free Key Value cache. PostgreSQL uses your existing Neon database.

1. Push the code, including `render.yaml`; keep `.env.production` and `.env.render` private.
2. Create a Render Blueprint from the repository. Enter `DJANGO_SECRET_KEY` and `DATABASE_URL` from `.env.render` when prompted. Redis is connected automatically.
3. For an existing manually created service, import `.env.render` under **Environment → Add from .env**, create a free Key Value instance in the same region, and set `REDIS_URL` to its internal connection URL. Redeploy the updated Docker image.
4. Add your domain under **Settings → Custom Domains** and apply the DNS records Render provides. Use `/api/health/` for the health check.

The Blueprint web service name is `ghanteyyy`; match the existing service name before using a Blueprint to manage it. The Render hostname is allowed automatically. Migrations run at startup; seed portfolio content and create a strong administrator after deployment.

Free Render storage does not preserve uploaded photos across restarts. External image storage is still needed for persistent admin uploads.
