FROM thespaghettidetective/web:base-1.4

WORKDIR /app
EXPOSE 3334

ADD . /app
RUN pip install -U pip
RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput -c
