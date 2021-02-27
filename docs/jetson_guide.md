# Run TSD server on Jetson Nano

Thanks to Raymond's and LyricPants work, you can now *easily* run TSD server on a 4GB Jetson Nano.

## Software requirements

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a software on you sd card, you will have to replace it with this one. Slow download of the software from Nvidia is normal. **Important:** Before you flash the new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.
  - [Flashing Software](https://www.balena.io/etcher/)
  - [SD Card Formater](https://www.sdcard.org/downloads/formatter/)

- Install all prerequisities, in one command!:
  - Run `wget -O jetson_TSD_install.sh https://raw.githubusercontent.com/LyricPants66133/Jetson_TSD_Fullinstall/master/full_install_script.sh && sudo sh ./jetson_TSD_install.sh`
  - Boot up your favorite streaming service and get a hot drink. This can take a long time.

## Start the server.

1. Create and modify a couple files in TheSpaghettiDetective repo that has been cloned already for you:

  - Create a `docker-compose.override.yml` file directly in the `TheSpaghettiDetective` folder.

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

  - Create a `docker-compose.override.yml` file in the `TheSpaghettiDetective/web` folder.

  - Modify file to include `FROM raymondh2/web:aarch64`

  - Create a `docker-compose.override.yml` file in the `TheSpaghettiDetective/ml_api` folder.

  - Modify file to include `FROM raymondh2/ml_api:jetson`
  
2. Run it!
 
 ```
 pipenv shell && cd TheSpaghettiDetective && sudo docker-compose up -d
 ```

3. Go refill your hot drink. Step 2 might also take a while.

## Set Docker to run on startup
In a terminal : `sudo systemctl enable docker`
and then reboot : `sudo reboot`


You can then follow the remaining steps by following the instructions in [README.md].
