# Santosh Karki Portfolio

React + Vite frontend, Django backend, and a React admin for content, photos, and messages.

## Local setup

Requires Python 3.13 and Node.js 22.12+ or 24. Run from the project root in PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements-dev.txt
Copy-Item .env.example .env
```

Set `DJANGO_SECRET_KEY` in `.env`. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

```powershell
.venv/Scripts/python backend/manage.py migrate
.venv/Scripts/python backend/manage.py seed_portfolio
.venv/Scripts/python backend/manage.py createsuperuser
.venv/Scripts/python backend/manage.py runserver 127.0.0.1:8000
```

In another terminal:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open [the portfolio](http://127.0.0.1:5173) or [admin](http://127.0.0.1:5173/admin/). Sign in with your admin email. Contact messages appear in the admin inbox; email delivery is not configured.

## Checks

```powershell
.venv/Scripts/python backend/manage.py test portfolio
.venv/Scripts/python -m ruff check backend deployment
npm --prefix frontend run format:check
npm --prefix frontend run build
```

See [deployment instructions](deployment/README.md) for production.
