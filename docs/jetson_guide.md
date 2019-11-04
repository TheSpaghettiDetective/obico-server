# Run TSD server on Jetson Nano

*Attribution: This guide is adopted from [Raymond's scripts](https://gist.github.com/RaymondHimle/5c06454f09f0e370ec0673835fb53dba).*

Thanks to Raymond's work, you can now easily run TSD server on Jetson. You only need to take one extra step to make it work:

- Open `docker-compose.yml` file.

- Find the following line and uncomment it:

```
...
# dockerfile: Dockerfile.aarch64   # Uncomment this line if you are running it on Jetson
...
```

You can then follow the remaining steps by following the instructions in [README.md].
