FROM python:3

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Required env vars and their default values

ENV FLASK_APP=server.py
ENV DEBUG=True
# ENV DEBUG=False
ENV REDIS_URL=redis://redis:6379

# Optional env vars

# ML_API_TOKEN=

EXPOSE 3333
CMD ["python",  "server.py"]
