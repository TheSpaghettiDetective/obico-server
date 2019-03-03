FROM python:3.6

RUN apt-get update && apt-get install -y vim ffmpeg
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333

RUN python manage.py collectstatic --noinput -c
