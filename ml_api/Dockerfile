FROM thespaghettidetective/ml_api_base:1.4
WORKDIR /app
EXPOSE 3333

ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN echo 'Downloading the latest failure detection AI model in Darknet format...'
RUN curl -o model/model-weights.darknet $(cat model/model-weights.darknet.url | tr -d '\r')
RUN echo 'Downloading the latest failure detection AI model in ONNX format...'
RUN curl -o model/model-weights.onnx $(cat model/model-weights.onnx.url | tr -d '\r')
