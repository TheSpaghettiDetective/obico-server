## Building ML backend images
The application images are built and published by CI (`.github/workflows/build-images.yaml`) on every push to the release branch. The arm64 legs run on GitHub's `ubuntu-24.04-arm` runners, which are free for public repositories; on a private fork they are billable, and a fork whose plan does not include them queues until the job times out. This page is about the ML *base* images, which are still built by hand. The GPU, Jetson and RK3588 variants start from one of them; the CPU image starts from `python:3.8-slim` and needs none. The web base is separate, built by `scripts/build_dockerfile_web_base.sh`.

To build them, use the provided [build_base_images.sh](../ml_api/scripts/build_base_images.sh) script.
It executes `docker` to build images, assign them tags and push into docker registry.
Script should be run from `ml_api` directory;

Arguments:
* -v VERSION argument should contain version number, like 1.3 or similar. It can also be `latest`
* -p PREFIX can be used to push images into a private repository or into a docker registry with a new name. Note that `ml_api/Dockerfile` hardcodes `thespaghettidetective/ml_api_base:1.4` in its `FROM`, so an image built under another prefix or version is not what a later `docker compose build ml_api` consumes unless you edit that line too.
* -i flag is used to help Docker work with insecure (like local private) repositories

The script builds one base per hardware target, and the tag suffix it produces is what selects a variant later: `ml_api/Dockerfile` takes an `IMAGE_TAG_SUFFIX` build arg and appends it to the base image tag, so `IMAGE_TAG_SUFFIX=-rk3588` builds against the RK3588 base. The suffix only picks the base; the RKNN model download keys off `rknn-toolkit-lite2` being importable in the base, which is what `ml_api/lib/rknn.py` needs, so the weights follow what the image can actually read whatever you named the tag.

Note that the `-rk3588` base is not published on Docker Hub — only `1.4` and `1.3` and their per-architecture tags are. `ml_api/Dockerfile` hardcodes the `thespaghettidetective` namespace in its `FROM`, so building that variant means producing the base locally under exactly the name it expects:

```bash
cd ml_api && docker build --platform linux/arm64 -f Dockerfile.base_rk3588 \
  -t thespaghettidetective/ml_api_base:1.4-rk3588 .
```

To run local registry, use: https://docs.docker.com/registry/deploying/
Ex: `docker run -d -p 5000:5000 --restart=always --name registry registry:2`
