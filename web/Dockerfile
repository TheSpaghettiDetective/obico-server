FROM thespaghettidetective/web:base

WORKDIR /app
COPY requirements.txt /app/
ADD . /app
EXPOSE 3334

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

RUN python manage.py collectstatic --noinput -c
