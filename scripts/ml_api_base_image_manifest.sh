#!/bin/bash -e

# Before you can run this script, go to ml_api folder and run
# 1. scripts/build_dockerfile_ml_api_base_arm64v8.sh on a Jetson Nano
# 2. scripts/build_dockerfile_ml_api_base_amd64.sh on a x84-based computer such as a PC or a (old) Mac
#

if [ "$#" -ne 1 ]; then
    echo "USAGE: ml_api_base_image_manifest.sh base_version"
    exit 1
fi

docker manifest create thespaghettidetective/ml_api:base-$1 --amend thespaghettidetective/ml_api:base-$1-linux-arm64v8 --amend thespaghettidetective/ml_api:base-$1-linux-amd64
docker manifest push thespaghettidetective/ml_api:base-$1
