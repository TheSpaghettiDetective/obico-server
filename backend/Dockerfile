# Use BASE_IMAGE arg to allow building locally and in GitHub actions
ARG BASE_IMAGE=thespaghettidetective/web:dev-django-4.2
FROM ${BASE_IMAGE}

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
ADD ./ /app

ENTRYPOINT ["/app/entrypoint.sh"]