FROM thespaghettidetective/web:base-1.15

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./ /app
RUN pip install -r requirements.txt
