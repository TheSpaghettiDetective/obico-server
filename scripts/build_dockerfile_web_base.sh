#!/bin/bash -e

docker buildx build backend --push --platform linux/arm64/v8,linux/amd64 -f backend/Dockerfile.base -t thespaghettidetective/web:base-$1
