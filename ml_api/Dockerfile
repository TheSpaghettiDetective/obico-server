ARG IMAGE_TAG_SUFFIX=
FROM thespaghettidetective/ml_api_base:1.4${IMAGE_TAG_SUFFIX}

RUN apt update && apt install -y curl

WORKDIR /app
EXPOSE 3333

# The URL files and requirements come first, so a source edit does not
# invalidate the pip layer or force a re-download of ~400MB of weights.
COPY requirements.txt /app/
COPY model/*.url model/*.sha256 /app/model/
COPY scripts/fetch_verified.sh /usr/local/bin/fetch_verified
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Each format is fetched only if this base can read it. The bases differ in
# which inference backends they carry, and a weight file no backend can load is
# dead payload — 200 MB for darknet, 200 MB for ONNX, 102 MB for RKNN, on
# images that go onto SD cards. Each probe asks about the thing that decides,
# not about the tag: the base decides whether a file is usable, and keying off
# the tag would ship a dead image to anyone who named the same base
# differently.
#
# Asked the way the loader asks: lib/rknn.py imports rknnlite.api, so that
# import is the question. Probing for the native librknnrt.so instead would
# pass on a base carrying the runtime without the Python package, where the
# 102 MB it gates is unreadable — the same mistake as keying off the tag, one
# level down. Where the runtime sits on disk is rknnlite's problem, not this
# file's.
#
# fetch_verified refuses an empty redirect body, an error page served with a
# 200, and a truncated transfer — see ml_api/scripts/fetch_verified.sh.
# Every one of these downloads carries a checksum, the only thing that fixes
# which bytes arrive. The S3 keys have a hash in the name, but that is a
# naming convention rather than content addressing — nothing stops the same
# key being rewritten. The RKNN URL is pinned to a commit, which does fix the
# content, and it still gets a checksum: a wrong model there is a green build
# and a container that dies on real hardware, which no CI job can see.
#
# Each digest sits in model/<name>.sha256 next to the URL it belongs to, so
# rotating one means editing two adjacent files and there is only ever one copy
# of the value. It used to be inline here and again in Containerfile.cpu, which
# needed a CI check to keep the two in step; a single source needs no check.
RUN mkdir -p /model_cache/ml_api/darknet /model_cache/ml_api/onnx /model_cache/ml_api/rknn \
 && if [ -e /darknet/libdarknet_gpu.so ] || [ -e /darknet/libdarknet_cpu.so ]; then \
      echo 'Downloading the latest failure detection AI model in Darknet format...'; \
      fetch_verified "$(tr -d '\r' < model/model-weights.darknet.url)" /model_cache/ml_api/darknet/model-weights.darknet 50000000 \
        "$(tr -d '\r' < model/model-weights.darknet.sha256)"; \
    else \
      echo 'No darknet library in this base; skipping its 200 MB of weights, which lib/darknet.py could not load here.'; \
    fi \
 && if python3 -c 'import onnxruntime' 2>/dev/null; then \
      echo 'Downloading the latest failure detection AI model in ONNX format...'; \
      fetch_verified "$(tr -d '\r' < model/model-weights.onnx.url)" /model_cache/ml_api/onnx/model-weights.onnx 50000000 \
        "$(tr -d '\r' < model/model-weights.onnx.sha256)"; \
    else \
      echo 'No onnxruntime in this base; skipping its 200 MB of weights, which lib/onnx.py could not load here.'; \
    fi \
 && if python3 -c 'import rknnlite.api' 2>/dev/null; then \
      echo 'Downloading the latest failure detection AI model in RKNN format...'; \
      fetch_verified "$(tr -d '\r' < model/model-weights.rknn.url)" /model_cache/ml_api/rknn/model-weights.rknn 50000000 \
        "$(tr -d '\r' < model/model-weights.rknn.sha256)"; \
    else \
      echo 'No rknn-toolkit-lite2 in this base; skipping the RKNN model, which lib/rknn.py could not load here.'; \
    fi

COPY . /app
