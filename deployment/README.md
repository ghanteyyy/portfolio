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
