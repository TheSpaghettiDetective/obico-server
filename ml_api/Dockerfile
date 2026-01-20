FROM thespaghettidetective/ml_api_base:1.4

RUN apt update && apt install -y curl

WORKDIR /app
EXPOSE 3333

ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /model_cache/ml_api/darknet /model_cache/ml_api/onnx \
 && echo 'Downloading the latest failure detection AI model in Darknet format...' \
 && curl -o /model_cache/ml_api/darknet/model-weights.darknet $(cat model/model-weights.darknet.url | tr -d '\r') \
 && echo 'Downloading the latest failure detection AI model in ONNX format...' \
 && curl -o /model_cache/ml_api/onnx/model-weights.onnx $(cat model/model-weights.onnx.url | tr -d '\r')
