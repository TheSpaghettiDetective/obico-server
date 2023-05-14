FROM thespaghettidetective/ml_api:base-1.1
WORKDIR /app
EXPOSE 3333

ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN wget --quiet -O model/model-weights.darknet $(cat model/model-weights.darknet.url | tr -d '\r')
RUN wget --quiet -O model/model-weights.onnx $(cat model/model-weights.onnx.url | tr -d '\r')
