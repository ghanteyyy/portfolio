FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY --from=frontend /app/frontend/dist ./frontend/dist
COPY deployment/gunicorn.conf.py /app/gunicorn.conf.py
COPY deployment/entrypoint.sh /app/entrypoint.sh
RUN DJANGO_DEBUG=true DJANGO_SECRET_KEY=build-only-not-used-by-the-running-server python backend/manage.py collectstatic --noinput \
    && groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir -p /app/backend/media /app/backend/staticfiles \
    && chown -R app:app /app/backend/media /app/backend/staticfiles \
    && chmod +x /app/entrypoint.sh
WORKDIR /app/backend
USER app
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--config", "/app/gunicorn.conf.py"]
