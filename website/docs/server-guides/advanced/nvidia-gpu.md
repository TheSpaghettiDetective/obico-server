---
title: Running Obico Server with Nvidia GPU acceleration
---

:::tip
This is only available on Linux based host machines.
:::

## Additional drivers {#additional-drivers}

In addition to the steps in [the basic installation steps](../install.md), you will need to:

- [CUDA driver](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) on your server. This driver may be already available on platforms such as JetPack 4.6.1 or higher.
- [nvidia-docker](https://github.com/NVIDIA/nvidia-docker). This driver may be already available on platforms such as JetPack 4.6.1 or higher.

## Make GPU available for the `ml_api` container {#make-gpu-available-for-the-ml_api-container}

You will need to create or update `docker-compose.override.yml` directly in `obico-server` folder to make GPU available for the `ml_api` container.

This section will only list a few common situations. If your situation is different, please join [the Obico discord server](https://obico.io/discord/) to figure out what will work for you, and hopefully contribute it back to this document afterward.

### For Debian-based PC with an NVidia GPU {#for-debian-based-pc-with-an-nvidia-gpu}

```yml title="docker-compose.override.yml"
version: '2.4'

services:
  ml_api:
    # enables GPU access for container
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### For JetPack based SBCs {#for-jetpack-based-sbcs}

```yml title="docker-compose.override.yml"
version: '2.4'

services:
  ml_api:
    runtime: nvidia
```

:::tip
Don't forget to restart the docker cluster by running `docker compose down && docker-compose up -d`.
:::

## Determine if GPU is being used {#determine-if-gpu-is-being-used}

The best way to determine if GPU is being used is by checking the `ml_api` container log:

```
cd obico-server
docker compose logs ml_api
```

If you see:

```
...
obico-server-ml_api-1  | ----- Trying to load weights: /app/lib/../model/model-weights.xxxx - **use_gpu = True** -----
...
Succeeded!
...
```

Then your self-hosted Obico Server is using your GPU.

If, instead, you see:

```
...
obico-server-ml_api-1  | ----- Trying to load weights: /app/lib/../model/model-weights.xxxx - **use_gpu = True** -----
...
Failed! ... some reason why it failed ...
...
obico-server-ml_api-1  | ----- Trying to load weights: /app/lib/../model/model-weights.xxxx - **use_gpu = False** -----
...
Succeeded!
...
```

Then somehow the Obico Server failed to load the GPU driver and hence fell back to using CPU.

## More details about the ML model and their supports of GPU {#more-details-about-the-ml-model-and-their-supports-of-gpu}

ML algorithms can be executed with different hardware and software options:

* x86_64 with CPU hardware without GPU, with `Darknet` or `ONNX` runtime.
* x86_64 with GPU (CUDA), with `Darknet` or `ONNX` runtime.
* ARM with GPU (CUDA), i.e. `Nvidia Jetson` devices with `Darknet` or `ONNX` runtime.

Darknet is written by Yolo2 author and you can find more details [here](https://github.com/AlexeyAB/darknet).
ONNX is Microsoft-powered set of libraries and standards to execute neural networks on a different hardware.
More details about ONNX can be found [here](https://onnxruntime.ai/).

Darknet is now stable implementation of TSD, while ONNX support is in beta stage now and may have some issues.

All suitable containers are built and now stored at docker.io registry, so you
probably don't need to compile them (takes hours).
