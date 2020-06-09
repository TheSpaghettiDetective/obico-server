#!/bin/bash

cd frontend

# Move cached node_modules over if on its 1st bootup to speed up the build process

if [[ -f /var/frontend/node_modules && ! -d frontend/node_modules ]]; then
    mv /var/frontend/node_modules .
fi

yarn && yarn build && cd ..

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py runserver --noreload 0.0.0.0:3334
