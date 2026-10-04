#!/bin/sh
# Starts SimBank in production mode: migrate, optional admin user, then gunicorn.
set -e

python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
fi

# One worker + several threads keeps the login/PIN rate-limiter consistent
# (it is kept in memory) and fits small free-tier containers.
exec gunicorn simbank.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --threads "${GUNICORN_THREADS:-8}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
