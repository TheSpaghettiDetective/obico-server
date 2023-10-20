#!/bin/bash

# Ensure all migrations are applied
python manage.py migrate

exec "$@"