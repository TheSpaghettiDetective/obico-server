#!/bin/bash -e

# This script is designed to run on x86 host

if [ "$#" -ne 1 ]; then
    echo "USAGE: build_dockerfile_ml_api_base_amd64.sh base_version"
    exit 1
fi

sudo docker build . -f Dockerfile.base_x86_64 -t thespaghettidetective/ml_api:base-$1-linux-amd64
sudo docker push thespaghettidetective/ml_api:base-$1-linux-amd64
