FROM python:3.6-alpine3.9

WORKDIR /app
EXPOSE 3334
RUN apk -U add bash vim ffmpeg postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev zlib-dev jpeg-dev
RUN pip install --upgrade pip

ADD requirements.txt .
RUN pip install -r requirements.txt && \
    apk --purge del .build-deps
