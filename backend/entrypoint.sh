#!/bin/bash

# Ensure all migrations are applied
python manage.py migrate
python manage.py collectstatic -v 2 --noinput

exec "$@"