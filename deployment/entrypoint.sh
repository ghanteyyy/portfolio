#!/bin/sh
set -eu
python manage.py migrate --noinput
python manage.py check --deploy --fail-level WARNING
python manage.py check_production
python manage.py seed_portfolio --if-empty
exec "$@"
