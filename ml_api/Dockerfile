FROM thespaghettidetective/ml_api_base:1.4
WORKDIR /app
EXPOSE 3333

COPY . /app
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN echo 'Downloading the latest failure detection AI model in Darknet format...'
RUN wget -O model/model-weights.darknet $(cat model/model-weights.darknet.url | tr -d '\r')
RUN echo 'Downloading the latest failure detection AI model in ONNX format...'
RUN wget -O model/model-weights.onnx $(cat model/model-weights.onnx.url | tr -d '\r')

CMD [ "gunicorn", "--bind", "0.0.0.0:3333", "--workers", "1", "wsgi" ]
