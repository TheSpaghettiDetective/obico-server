FROM thespaghettidetective/web:base-4

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
ADD ./ /app

ENTRYPOINT ["/app/entrypoint.sh"]