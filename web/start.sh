#!/bin/bash

if [ "x$1" = 'x-c' ]; then
  celery -A config worker -l info
else
  python manage.py runserver 0.0.0.0:3334
fi
