FROM thespaghettidetective/ml_api:base
WORKDIR /app
EXPOSE 3333

ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN wget --quiet -O model/model.weights $(cat model/model.weights.url | tr -d '\r')
