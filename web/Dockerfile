FROM python:3

RUN apt-get update && apt-get install -y vim

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333

ENV FLASK_APP=server.py
ENV REDIS_URL=redis://redis:6379

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:$PORT"]
