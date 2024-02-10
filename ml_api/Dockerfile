ARG BASE_TAG="1.3"
FROM thespaghettidetective/ml_api_base:${BASE_TAG}
LABEL base-tag="${BASE_TAG}"

WORKDIR /app
EXPOSE 3333

COPY . /app
# Add opencv2 dependencies
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && pip install --upgrade --no-cache-dir pip==23.3.2 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

# check if we can load app, if any python import fails then it will fail image build
RUN gunicorn --bind 0.0.0.0:3333 --workers 1 wsgi --check-config --preload
