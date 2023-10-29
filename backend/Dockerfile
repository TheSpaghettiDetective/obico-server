FROM thespaghettidetective/web:base-1.14

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
ADD ./ /app
