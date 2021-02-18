# Run TSD server on Jetson Nano

Thanks to Raymond's work, you can now easily run TSD server on a 4GB Jetson.

## Software requirements

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a software on you sd card, you will have to replace it with this one. Slow download of the software from Nvidia is normal. **Important:** Before you flash the new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.
  - [Flashing Software](https://www.balena.io/etcher/)
  - [SD Card Formater](https://www.sdcard.org/downloads/formatter/)

- pip and pip3.
    - Run `sudo apt install python-pip`
    - Run `sudo apt install python-pip3`

- [Docker-compose](https://docs.docker.com/compose/install/#install-using-pip) (Docker is already pre-loaded with JetPack). Currently, there is no established method of installing Docker-compose that we know will work first try for the newest version of JetPack. However, we do have a list of methods/resources that can be referred to on how to do this.
    - Method 1: [pipenv](https://docs.docker.com/compose/install/#install-using-pip) (Alternative install options)
        - Run `pip install --user pipenv` to install pipenv.
        - Run `sudo pipenv install docker-compose` to (hopefully) install docker-compose. This may take a while.

    - Method 2: [pip](https://docs.docker.com/compose/install/#install-using-pip) (Alternative install options)
        - Run `sudo pip install docker-compose` to (hopefully) install docker-compose.
   
		- Method 3: [pip3](https://docs.docker.com/compose/install/#install-using-pip) (Alternative install options)
        - Run `sudo pip3 install docker-compose` to (hopefully) install docker-compose.
   
    - Method 4: [Install some required dependencies before running the install](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-jetson-nano-4gb-2gb-in-2-simple-steps-1f4i). Follow the listed guide.

    - Method 5: [Aquire help from the Offical Discord](https://discord.gg/5bnFgzGWHY). Please first look at [this](https://discord.com/channels/614543405724205137/648759742881071124/811686583043620923) thread to see if any part of it may help you before you post. 
  
- git ([how to install](https://git-scm.com/downloads)).

## Get the code and start the server.

1. Get the code:

```
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
```

2. Create a couple files:

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

  - Modify file to include `FROM raymondh2/web:aarch64` `FROM raymondh2/ml_api:jetson`
  
 3. Run it!
 
 ```
 cd TheSpaghettiDetective && sudo docker-compose up -d
 ```

4. Go grab a coffee. Step 3 will take 15-30 minutes.

You can then follow the remaining steps by following the instructions in [README.md].
