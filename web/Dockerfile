FROM python:3

RUN apt-get update && apt-get install -y vim
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt


# = (0.27 - 0.07): 0.27 - optimal THRESHOLD_LOW in hyper params grid search; 0.07 - 2 x median of rolling_mean_short
ENV THRESHOLD_LOW=0.20
# = (0.56 - 0.07): 0.56 - optimal THRESHOLD_HIGH in hyper params grid search; 0.07 - 2 x median of rolling_mean_short
ENV THRESHOLD_HIGH=0.49

EXPOSE 3333

RUN python manage.py collectstatic --noinput -c

CMD ["sh", "-c", "python manage.py migrate && newrelic-admin run-program gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:3334"]
