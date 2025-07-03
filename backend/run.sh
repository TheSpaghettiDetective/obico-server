#!/bin/sh

OBICO_CONTAINER=${OBICO_CONTAINER:-$1}
if [ "${OBICO_CONTAINER}" = "tasks" ]; then
  celery -A config worker --beat -l info -c 2 -Q realtime,celery
elif [ "${OBICO_CONTAINER}" = "web" ]; then
  # Implementation from https://github.com/imagegenius/docker-obico
  mkdir /data/media
  mkdir /app/static_build
  ln -s data/media /app/static_build/media

  python manage.py migrate && python manage.py collectstatic -v 2 --noinput && daphne -b 0.0.0.0 -p 3334 config.routing:application
fi
