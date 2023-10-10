FROM thespaghettidetective/web:base-4

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements-4.x.txt /app
RUN pip install -r requirements-4.x.txt
ADD ./ /app

ENTRYPOINT ["/app/entrypoint.sh"]