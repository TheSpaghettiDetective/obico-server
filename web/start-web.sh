#!/bin/bash

cd frontend

# Move cached node_modules over if on its 1st bootup to speed up the build process

if [ -d /var/frontend/node_modules -a ! -d /app/frontend/node_modules ]; then
    rm -rf /app/frontend/node_modules
    mv /var/frontend/node_modules /app/frontend/
fi

yarn && yarn build && cd ..

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py runserver --noreload 0.0.0.0:3334
