---
title: Running Obico Server with Nvidia GPU acceleration
---

This is only available on Linux based host machines

In addition to the steps in [the basic installation steps](../install.md), you will need to:

- [Install Cuda driver](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) on your server.
- [Install nvidia-docker](https://github.com/NVIDIA/nvidia-docker).
- Run this command in `obico-server` directory:
```
cat <<EOT >docker-compose.override.yml
version: '2.4'

services:
  ml_api:
    runtime: nvidia
    environment:
        HAS_GPU: 'True'
EOT
```
- Restart the docker cluster by running `docker compose down && docker compose up -d`
