ARG BASE_TAG="1.3"
FROM thespaghettidetective/ml_api_base:${BASE_TAG}
LABEL base-tag="${BASE_TAG}"

WORKDIR /app
EXPOSE 3333

COPY . /app
RUN pip install --upgrade --no-cache-dir pip==23.3.2 \
    && pip install --no-cache-dir -r requirements.txt

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# fetch each model as separate layer, improces layer reuse
RUN echo 'Downloading the latest failure detection AI model in Darknet format...' \
    && wget --progress=dot:giga -O model/model-weights.darknet -i model/model-weights.darknet.url
RUN echo 'Downloading the latest failure detection AI model in ONNX format...' \
    && wget --progress=dot:giga -O model/model-weights.onnx -i model/model-weights.onnx.url

ARG GIT_SOURCE
ARG GIT_COMMIT
LABEL org.opencontainers.image.source="${GIT_SOURCE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
