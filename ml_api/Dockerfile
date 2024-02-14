FROM thespaghettidetective/ml_api_base:1.4
WORKDIR /app
EXPOSE 3333

COPY . /app
RUN pip install --no-cache-dir --upgrade pip==23.3.2 \
    && hash -r \
    && pip install  --no-cache-dir  -r requirements.txt

RUN echo 'Downloading the latest failure detection AI model in Darknet format...' \
    && wget --progress=dot:giga -O model/model-weights.darknet -i model/model-weights.darknet.url
RUN echo 'Downloading the latest failure detection AI model in ONNX format...' \
    && wget --progress=dot:giga -O model/model-weights.onnx -i model/model-weights.onnx.url

# do not write .pyc files which is useful in read-only containers
ENV PYTHONDONTWRITEBYTECODE=1

# define where darknet is stored in container image
ENV DARKNET_PATH=/darknet

# check if we can load app, if any python import fails then it will fail image build
RUN gunicorn --bind 0.0.0.0:3333 --workers 1 wsgi --check-config --preload -e DARKNET_PATH=$DARKNET_PATH

