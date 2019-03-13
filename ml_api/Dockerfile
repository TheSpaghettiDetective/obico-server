FROM python:3

ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 3333
CMD ["sh", "-c", "newrelic-admin run-program python server.py"]
