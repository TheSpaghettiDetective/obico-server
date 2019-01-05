FROM python:3

RUN apt-get update && apt-get install -y vim

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 3333
CMD ["python",  "server.py"]
