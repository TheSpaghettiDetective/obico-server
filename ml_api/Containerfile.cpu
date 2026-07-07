# CPU-only build of the Obico ML failure-detection API.
#
# The GPU image (ml_api/Dockerfile, built on the CUDA ml_api_base) bakes in the
# CUDA/cuDNN runtime plus both the darknet and ONNX inference runtimes — roughly
# 3 GB compressed, most of which a CPU-only deployment never executes. This
# image drops CUDA and darknet entirely: lib.detection_model.load_net() falls
# back to the ONNX net when darknet cannot be imported, so ONNX Runtime (CPU)
# alone serves inference. The result is an order of magnitude smaller and builds
# without an NVIDIA toolchain.
#
# Python 3.8 mirrors the runtime of the CUDA base image (Ubuntu 20.04). Keep it
# in lockstep with that base and with the pinned inference dependencies below.
FROM python:3.8-slim

# libgomp1: OpenMP runtime required by ONNX Runtime.
# libglib2.0-0: shared object required by opencv-python-headless.
RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
        curl ca-certificates libgomp1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU inference stack: onnxruntime (not onnxruntime-gpu) and the headless OpenCV
# build (no GUI/X11 dependencies). Pinned to releases that ship cp38 wheels.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        onnxruntime==1.16.3 \
        opencv-python-headless==4.9.0.80

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY . /app

# Pre-fetch the ONNX model so the container needs no network at startup. The
# darknet weights the GPU image also downloads are intentionally omitted.
RUN mkdir -p /model_cache/ml_api/onnx \
    && curl --fail --silent --show-error --location \
        --output /model_cache/ml_api/onnx/model-weights.onnx \
        "$(tr -d '\r' < model/model-weights.onnx.url)"

EXPOSE 3333

CMD ["gunicorn", "--bind", "0.0.0.0:3333", "--workers", "1", "wsgi"]
