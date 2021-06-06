#!/bin/bash -e

docker buildx build web --push --platform linux/arm64/v8,linux/amd64 -f Dockerfile.base -t thespaghettidetective/web:base-$1
