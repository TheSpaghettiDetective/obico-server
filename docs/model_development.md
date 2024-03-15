# ML model development guide

The following instructions will assist you in making changes to the ML model or its integration into the Spaghetti Detective service.

*If you follow this guide and run into problems, please seek help at: https://obico.io/discord*

## Overview & Architecture

Model data, libraries, and scripts are located int `ml_api/`.

The TSD model uses a convolutional neural network adapted from [YOLOv2](https://pjreddie.com/darknet/yolov2/), which is a machine learning model designed for the task of object detection and localization in images.

The model is run using https://github.com/AlexeyAB/darknet. **This is a fork of the [original Darknet framework](https://pjreddie.com/darknet/) with substantial changes made to how the model is loaded and evaluated**, and running on the "old" darknet will cause weird failures as a result.

Darknet itself is a C-based framework that compiles to a [shared library](https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html) which we then access in Python via the [ctypes](https://docs.python.org/3/library/ctypes.html) library (see `ml_api/lib/detection_model.py`). These shared libraries live in `ml_api/bin/*.so` and are specific to the architecture of whatever's hosting the `ml_api` docker container.

The model is set up and hosted via `server.py`, which provides a `/p/?img=...` URL endpoint on port `3333` of the `ml_api` container.

When passed an image URL, the server:

1. Fetches the image and converts it to an OpenCV image object
2. Runs the darknet detection model, which:
   1. formats the image to match the model input layer
   2. evaluates the model via GPU
   3. filters the results (including via [non-max suppression](https://learnopencv.com/non-maximum-suppression-theory-and-implementation-in-pytorch/) and probability thresholds)
   4. returns one or more bounding boxes which are likely to contain spaghetti
2. Formats the results so that they are easily parsable by the web server, and returns them as a JSON array of `[{category_name, detection_probability, bounding_box}]`. There's currently only one category of "failure", i.e. failure/spaghetti detected.

## Building and running `ml_api` locally

The `ml_api` container is made up of a base docker image that provides ML dependencies and an additional image that actually installs our model.

To build the base image locally (replacing `_aarch64` with your architecture of choice as per `uname -a`):

```
cd ml_api && docker build --tag thespaghettidetective/ml_api:base-1.1 -f Dockerfile.base_aarch64 .
```

To build the main image locally:

```
docker-compose build ml_api
```

You can use the usual `docker-compose up` command to launch the whole ensemble including web and task containers, but the web container in particular takes several minutes to initialize.

For rapid development, it's faster to launch `ml_api` on its own, mounting the local directory and exposing the web port:

```
docker-compose run --service-ports --volume=./ml_api:/app ml_api /bin/bash

# Run this command when the container starts, and re-run it whenever you make a code change
gunicorn --bind 0.0.0.0:3333 --workers 1 wsgi
```

When you see `Loaded - names_list: model/names, classes = 1` in the logs, the model server should be ready.

You can verify the server is up by going to http://localhost:3333/hc/ in your browser (or replacing `localhost` with the host name if developing remotely). It should return a white page with the word `ok`.

If you want to test whether an image produces a detection, try visiting this link in a browser:

http://localhost:3333/p/?img=https://user-images.githubusercontent.com/607666/154857506-f67fe00c-a423-4a12-9ee0-8dced1b72968.png

You should see a result that looks like:

```json
{
  "detections": [
    [
      "failure",
      12.82,
      [
        407.9657897949219,
        304.8846740722656,
        26.581132888793945,
        74.72808074951172
      ]
    ],
    [
      "failure",
      14.81,
      [
        260.202880859375,
        217.86647033691406,
        31.743249893188477,
        62.16251754760742
      ]
    ]
  ]
}
```

## Rebuilding darknet shared objects

You may wish to rebuild the `ml_api/bin/*.so` files when updates to other dependencies of darknet - such as CUDART - cause `ml_api` to crash when attempting to load or run the model. This is especially true when hosting on the Jetson Nano, which regularly updates their [developer kit image](https://developer.nvidia.com/embedded/downloads) to use newer versions of these dependencies which may not be backwards-compatible (see e.g. [this issue](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/552)).

Original instructions on how to build these libraries are available [here](https://github.com/AlexeyAB/darknet#how-to-use-yolo-as-dll-and-so-libraries).

Run these commands on your host device to build the darknet `*.so` file and install it within the Spaghetti Detective repo:

```shell
# Ensure nvcc is added to path
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export TSD_PATH=<path_to_your_spaghetti_detective_repository>

# Clone the darknet repository
git clone https://github.com/AlexeyAB/darknet.git && cd darknet

# Here, edit the makefile and set GPU=1 and LIBSO=1 at the top
vim Makefile

# Build the repository using all of the CPU cores on the host - this may take a few minutes
make -j$(nproc)

# Copy the built library to the correctly named location within ml_api/bin/
PLATFORM=$(python3 -c "import platform; print(platform.machine())")
cp libdarknet.so $TSD_PATH/ml_api/bin/model_gpu_$PLATFORM.so

# Rebuild the container so it contains the new shared library.
cd $TSD_PATH && docker-compose build ml_api
```

## Troubleshooting `*.so` dependencies

If you get errors relating to other missing `*.so` files, you can confirm they're missing dependencies of the darknet `*.so` file by checking with `ldd`.

Here's an example for an aarch64 device:

```shell
$ docker exec -it --tty thespaghettidetective_ml_api_1 /bin/bash -c "ldd bin/model_gpu_aarch64.so"
```

You should see dependencies listed like so:

```shell
linux-vdso.so.1 (0x0000007fac03c000)
libcuda.so.1 => /usr/lib/aarch64-linux-gnu/tegra/libcuda.so.1 (0x0000007faac5f000)
libcudart.so.10.2 => /usr/local/cuda-10.2/targets/aarch64-linux/lib/libcudart.so.10.2 (0x0000007faabbe000)
libcublas.so.10 => /usr/local/cuda-10.2/targets/aarch64-linux/lib/libcublas.so.10 (0x0000007fa5e56000)
libcurand.so.10 => /usr/local/cuda-10.2/targets/aarch64-linux/lib/libcurand.so.10 (0x0000007fa1d25000)
...
```

This can happen when - for whatever reason - the symlinks for a `.so` file aren't populated by nvidia-docker in the same way as on the host. This has happened before on the Jetson Nano with libcuda.so.1 and libnvidia-ptxjitcompiler.so.1 in /usr/lib/aarch64-linux-gnu/tegra of the container, specifically with these errors:

For missing link to libnvidia-ptxjitcompiler.so.1:

```
ml_api_1  |  CUDA Error: PTX JIT compiler library not found
```

For missing link ot `libcuda.so.1`:

```
ml_api_1  | OSError: libcuda.so.1: cannot open shared object file: No such file or directory
```

A (hacky) workaround to this is to force create these symlinks before running the `gunicorn` container command, like so:

```
# in docker-compose.yaml
services:
  ml_api:
    ...
    command: bash -c "ln -sf /usr/lib/aarch64-linux-gnu/tegra/libcuda.so /usr/lib/aarch64-linux-gnu/tegra/libcuda.so.1 && ln -s /usr/lib/aarch64-linux-gnu/tegra/libnvidia-ptxjitcompiler.so.440.18 /usr/lib/aarch64-linux-gnu/tegra/libnvidia-ptxjitcompiler.so.1 && gunicorn --bind 0.0.0.0:3333 --workers 1 wsgi"
```

## Troubleshooting segmentation faults

Segfaults can happen when there is a mismatch in the compiled darknet shared library and the python code attempting to run it. You may not get a lot of detail if you're running a python script and the segfault happens in C code - in this case, prepending your shell command with `PYTHONFAULTHANDLER=1` can increase the amount of information you get back (details [here](https://docs.python.org/3/library/faulthandler.html)).

If the segfault appears to be about trying to invoke a method that the `*.so` file doesn't have, you can run `nm -D bin/model_aarch64.so` to see inside the binary and confirm whether or not this is actually the case.
