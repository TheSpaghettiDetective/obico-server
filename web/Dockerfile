FROM python:3

RUN apt-get update && apt-get install -y vim
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333

ENV ALERT_P_THRESHOLD=0.45

RUN python manage.py collectstatic --noinput -c

CMD ["sh", "-c", "python manage.py migrate && newrelic-admin run-program gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:3334"]
