# Use BASE_IMAGE arg to allow building locally and in GitHub actions
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
ADD ./ /app

RUN python manage.py collectstatic -v 2 --noinput

ENTRYPOINT ["/app/entrypoint.sh"]