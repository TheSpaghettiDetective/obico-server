FROM thespaghettidetective/web:base

WORKDIR /app
EXPOSE 3334

ADD . /app
RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput -c
