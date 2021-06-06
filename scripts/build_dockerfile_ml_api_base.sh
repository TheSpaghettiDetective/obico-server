#!/bin/bash -e

docker manifest create thespaghettidetective/ml_api:base-$1 --amend thespaghettidetective/ml_api:base-$1-linux-arm64v8 --amend thespaghettidetective/ml_api:base-$1-linux-amd64
docker manifest push thespaghettidetective/ml_api:base-$1
