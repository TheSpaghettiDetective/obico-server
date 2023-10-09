FROM thespaghettidetective/web:base-1.13

WORKDIR /app
EXPOSE 3334

ADD . /app
RUN pip install -U pip
RUN pip install -r requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]