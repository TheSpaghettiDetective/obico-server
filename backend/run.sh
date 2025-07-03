#!/bin/sh
set -e

OBICO_CONTAINER=${OBICO_CONTAINER:-$1}
if [ "${OBICO_CONTAINER}" = "tasks" ]; then
  celery -A config worker --beat -l info -c 2 -Q realtime,celery
elif [ "${OBICO_CONTAINER}" = "web" ]; then
  python manage.py migrate 
  python manage.py collectstatic -v 2 --noinput 
  
  # Implementation from https://github.com/imagegenius/docker-obico
  [ -d /data/media ] || mkdir /data/media
  rm -r /app/static_build/media
  ln -s data/media /app/static_build/media

  daphne -b 0.0.0.0 -p 3334 config.routing:application
fi
