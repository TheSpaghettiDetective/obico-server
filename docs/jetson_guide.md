# Run TSD server on Jetson Nano

*Attribution: This guide is adopted from [Raymond's scripts](https://gist.github.com/RaymondHimle/5c06454f09f0e370ec0673835fb53dba).*

Thanks to Raymond's work, you can now easily run TSD server on Jetson.

## Software requirements

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a software on you sd card, you will have to replace it with this one. **Important:** Before you flash the new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.
  - [Flashing Software](https://www.balena.io/etcher/)
  - [SD Card Formater](https://www.sdcard.org/downloads/formatter/)

- [Docker and Docker-compose](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-jetson-nano-4gb-2gb-in-2-simple-steps-1f4i). But you don't have to understand how Docker or Docker-compose works. This step may also take a while to complete.

- git ([how to install](https://git-scm.com/downloads)).

## Get the code and start the server.

1. Get the code:

```
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
```

2. Modify and create a couple files:

  - Create and or open `docker-compose.override.yml` file. (this file can be found directly in the `TheSpaghettiDetective` folder. If not there, create it).

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
  
 3. Run it!
 
 ```
 cd TheSpaghettiDetective && sudo docker-compose up -d
 ```

4. Go grab a coffee. Step 3 will take 15-30 minutes.

You can then follow the remaining steps by following the instructions in [README.md].
