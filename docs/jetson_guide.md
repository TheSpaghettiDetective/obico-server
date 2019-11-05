# Run TSD server on Jetson Nano

*Attribution: This guide is adopted from [Raymond's scripts](https://gist.github.com/RaymondHimle/5c06454f09f0e370ec0673835fb53dba).*

Thanks to Raymond's work, you can now easily run TSD server on Jetson. You only need to take one extra step to make it work:

- Create and or open `docker-compose.override.yml` file.

- Modify file to include:

```
version: '2.4'

x-web-defaults: &web-defaults
  build:
    dockerfile: Dockerfile.base

services:
  ml_api:
    build:
      context: ml_api
      dockerfile: Dockerfile.aarch64
    environment:
        HAS_GPU: 'True'
    runtime: nvidia
```

You can then follow the remaining steps by following the instructions in [README.md].
