FROM thespaghettidetective/web:base-1.18

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip pipenv==2022.12.19

ADD ./ /app
RUN pip install -r requirements.txt
