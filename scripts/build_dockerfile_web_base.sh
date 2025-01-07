#!/bin/bash -e

BUILDKIT_MAX_PARALLELISM=1 docker buildx build backend --progress=plain --push --platform linux/arm64/v8,linux/amd64 -f backend/Dockerfile.base -t thespaghettidetective/web:base-$1
