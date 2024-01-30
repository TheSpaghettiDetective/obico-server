FROM thespaghettidetective/ml_api_base:1.3
WORKDIR /app
EXPOSE 3333

COPY . /app
RUN pip install --upgrade --no-cache-dir pip==23.3.2 \
    && pip install --no-cache-dir -r requirements.txt

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo 'Downloading the latest failure detection AI model in Darknet format...' \
    && wget --progress=dot:giga -O model/model-weights.darknet -i model/model-weights.darknet.url
RUN echo 'Downloading the latest failure detection AI model in ONNX format...' \
    && wget --progress=dot:giga -O model/model-weights.onnx -i model/model-weights.onnx.url
