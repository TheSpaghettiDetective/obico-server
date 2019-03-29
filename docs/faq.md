# Frequently Asked Question

## How do I run TSD on a server with GPU?

Great to know you are ready for some challenge! ;)

### On Linux

In addition to the steps in [README](../README.md), you will need to:

- [Install Cuda driver](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) on your server.
- [Install nvidia-docker](https://github.com/NVIDIA/nvidia-docker).
- Run this command in `TheSpaghettiDetective` directory:
```
cat >docker-compose.override.yml <<EOF
version: '2.4'

services:
  ml_api:
    runtime: nvidia
EOF
```
- Restart the docker cluster by running `docker-compose down && docker-compose up -d`


### On Windows (???)
