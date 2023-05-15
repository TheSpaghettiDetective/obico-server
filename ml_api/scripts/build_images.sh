#!/bin/bash -e


if [ "$#" -ne 1 ]; then
    echo "USAGE: build_images.sh base_version"
    exit 1
fi

# VARIANT=darknet_cpu
# VERSION_BASE=thespaghettidetective/ml_api_${VARIANT}:$1
# docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
# #docker manifest create ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64
# #docker manifest push ${VERSION_BASE}
#
# VARIANT=darknet_gpu
# VERSION_BASE=thespaghettidetective/ml_api_${VARIANT}:$1
# docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
# docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT}_l4t .
# #docker manifest create ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8
# #docker manifest push ${VERSION_BASE}
#
VARIANT=onnx_cpu
VERSION_BASE=thespaghettidetective/ml_api_${VARIANT}:$1
# docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
# docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT} .
# docker build --platform linux/arm/v7 -t ${VERSION_BASE}-linux-armv7 --target ml_api_${VARIANT} .
# this may take a lot of time
docker build --platform linux/arm/v7 -t ${VERSION_BASE}-linux-armv7 --target ml_api_${VARIANT}_arm32 .
#docker manifest create ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8  --amend ${VERSION_BASE}-linux-arm32v7
#docker manifest push ${VERSION_BASE}

VARIANT=onnx_gpu
VERSION_BASE=thespaghettidetective/ml_api_${VARIANT}:$1
docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT}_l4t .
#docker manifest create ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8
#docker manifest push ${VERSION_BASE}
