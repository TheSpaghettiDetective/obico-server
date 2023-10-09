FROM thespaghettidetective/web:base-3.0

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements-3.x.txt /app
RUN pip install -r requirements-3.x.txt
RUN pip uninstall -y django-channels-presence && pip install django-channels-presence
ADD ./ /app

ENTRYPOINT ["/app/entrypoint.sh"]