FROM python:3

RUN apt-get update && apt-get install -y vim
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333

# Required env vars and their default values

ENV DEBUG=True
# ENV DEBUG=False
ENV SITE_USES_HTTPS=False
# ENV SITE_USES_HTTPS=True
ENV SOCIAL_LOGIN=False
# ENV SOCIAL_LOGIN=True

ENV REDIS_URL=redis://redis:6379
ENV DATABASE_URL=sqlite:////app/db.sqlite3
ENV INTERNAL_MEDIA_HOST=http://web:3334
ENV ML_API_HOST=http://ml_api:3333

# Optional env vars

# AZURE_STORAGE_CONNECTION_STRING=
# AZURE_STORAGE_CONTAINER=
# ENALBE_HISTORY=False
# EMAIL_HOST=
# EMAIL_HOST_USER=
# EMAIL_HOST_PASSWORD=
# EMAIL_PORT=
# EMAIL_USE_TLS=True
# DEFAULT_FROM_EMAIL=changeme@example.com
# ML_API_TOKEN=

RUN python manage.py collectstatic --noinput -c

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:3334"]
