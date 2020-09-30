# Run TSD server on Jetson Nano

*Attribution: This guide is adopted from [Raymond's scripts](https://gist.github.com/RaymondHimle/5c06454f09f0e370ec0673835fb53dba).*

Thanks to Raymond's work, you can now easily run TSD server on Jetson. You only need to take one extra step to make it work:

- Create and or open `docker-compose.override.yml` file.

- Modify file to include:

```
version: '2.4'

services:
  ml_api:
    build:
      context: ml_api
    environment:
        HAS_GPU: 'True'
    runtime: nvidia
```

- Edit `web/Dockerfile`.

- Change `FROM thespaghettidetective/web:base-1.1` to `FROM raymondh2/web:aarch64`

- Edit `ml_api/Dockerfile`.

- Change `FROM thespaghettidetective/ml_api:base` to `FROM raymondh2/ml_api:jetson`

You can then follow the remaining steps by following the instructions in [README.md].
