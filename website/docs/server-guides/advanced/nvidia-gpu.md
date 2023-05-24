---
title: Running Obico Server with Nvidia GPU acceleration
---

:::tip
This is only available on Linux based host machines.
:::

## Additional drivers

In addition to the steps in [the basic installation steps](../install.md), you will need to:

- [CUDA driver](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) on your server. This driver may be already available on platforms such as JetPack 4.6.1 or higher.
- [nvidia-docker](https://github.com/NVIDIA/nvidia-docker). This driver may be already available on platforms such as JetPack 4.6.1 or higher.

## Make GPU available for the `ml_api` container

You will need to create or update `docker-compose.override.yml` directly in `obico-server` folder to make GPU available for the `ml_api` container.

This section will only list a few common situations. If your situation is different, please join [the Obico discord server](https://obico.io/discord/) to figure out what will work for you, and hopefully contribute it back to this document afterward.

### For Debian-based PC with an NVidia GPU

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

### For JetPack based SBCs

```yml title="docker-compose.override.yml"
version: '2.4'

services:
  ml_api:
    runtime: nvidia

:::tip
Don't forget to restart the docker cluster by running `docker compose down && docker-compose up -d`.
:::
