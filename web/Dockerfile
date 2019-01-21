FROM python:3

RUN apt-get update && apt-get install -y vim

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333

ENV FLASK_APP=server.py
ENV EXTERNAL_MEDIA_HOST=http://localhost:3334
ENV REDIS_URL=redis://redis:6379

CMD ["python",  "server.py"]
