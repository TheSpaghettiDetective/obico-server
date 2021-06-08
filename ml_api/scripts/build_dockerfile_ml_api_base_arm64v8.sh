#!/bin/bash -e

# This script is designed to run on Jetson Nano only

if [ "$#" -ne 1 ]; then
    echo "USAGE: build_dockerfile_ml_api_base_arm64v8.sh base_version"
    exit 1
fi

sudo docker build . -f Dockerfile.base_aarch64 -t thespaghettidetective/ml_api:base-$1-linux-arm64v8
sudo docker push thespaghettidetective/ml_api:base-$1-linux-arm64v8
