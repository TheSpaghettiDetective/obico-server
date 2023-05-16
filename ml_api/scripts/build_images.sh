#!/bin/bash -e



VERSION=
PREFIX=thespaghettidetective
INSECURE=

while getopts v:p:i flag
do
    case "$flag" in
        v) VERSION=${OPTARG};;
        p) PREFIX=${OPTARG};;
        i) INSECURE="--insecure"
    esac
done

if [ -z "$VERSION" ]; then
    echo "USAGE: build_images.sh -v base_version [-p prefix] [-i]"
    echo "-v base_version: required, defines the version of the image"
    echo "-p prefix: optional, can be used to push images into private repository, ex: localhost:5000/obico"
    echo "-i: optional, adds --insecure flag to manifest create command, helps to resolve 'manifest not found' error if not using https"
    exit 1
fi

VARIANT=darknet_cpu
VERSION_BASE=${PREFIX}/ml_api_${VARIANT}:${VERSION}
echo Building $VERSION_BASE
docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-amd64
docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-arm64v8
docker manifest create ${INSECURE} ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8
docker manifest push ${VERSION_BASE}

VARIANT=darknet_gpu
VERSION_BASE=${PREFIX}/ml_api_${VARIANT}:${VERSION}
echo Building $VERSION_BASE
docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-amd64
# Does not work for now
# docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT}_l4t .
# docker push ${VERSION_BASE}-linux-arm64v8
docker manifest create ${INSECURE} ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64
#--amend ${VERSION_BASE}-linux-arm64v8
docker manifest push ${VERSION_BASE}

VARIANT=onnx_cpu
VERSION_BASE=${PREFIX}/ml_api_${VARIANT}:${VERSION}
echo Building $VERSION_BASE
docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-amd64
docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-arm64v8
docker manifest create ${INSECURE} ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8 
docker manifest push ${VERSION_BASE}

VARIANT=onnx_gpu
VERSION_BASE=${PREFIX}/ml_api_${VARIANT}:${VERSION}
echo Building $VERSION_BASE
docker build --platform linux/amd64 -t ${VERSION_BASE}-linux-amd64 --target ml_api_${VARIANT} .
docker push ${VERSION_BASE}-linux-amd64
docker build --platform linux/arm64/v8 -t ${VERSION_BASE}-linux-arm64v8 --target ml_api_${VARIANT}_l4t .
docker push ${VERSION_BASE}-linux-arm64v8
docker manifest create ${INSECURE} ${VERSION_BASE} --amend ${VERSION_BASE}-linux-amd64 --amend ${VERSION_BASE}-linux-arm64v8
docker manifest push ${VERSION_BASE}
