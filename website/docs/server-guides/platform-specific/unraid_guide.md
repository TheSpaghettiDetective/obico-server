# Run obico-server on Unraid

If video is your cup of tea, follow [this awesome video guide](https://www.youtube.com/watch?v=B2gjxL0MgEo) put together by Ricky at [SNR Tech Bytes](https://www.snrtechbytes.com/).Thank you Ricky!


## Install docker-compose {#install-docker-compose}

Since the original creation of this guide a great new tool to install Docker-Compose on Unraid has been released. It can be installed through the normal process of going to the Apps tab and doing a search for "Docker Compose Manager" and installing the plugin. The below instructions will still work if you'd like to do it manually, however, suggest using the Plug-In instead. Support can be found at the Unraid forums for the [Docker Compose Manager](https://forums.unraid.net/topic/114415-plugin-docker-compose-manager/).

#### Old process to install Docker-Compose: {#old-process-to-install-docker-compose}

To run obico-server on Unraid, you first must install Docker-Compose on the server. This can be done following the usual instructions found on the [Docker-Compose Install Guide](https://docs.docker.com/compose/install/#install-compose-on-linux-systems).

```Bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

However, because Unraid boots from a USB to RAM, this installation will not be persistent. To make sure that Docker-Compose gets installed every time the server boots, follow the following steps from [this forum post](https://forums.unraid.net/topic/91436-is-docker-compose-available-on-unraid/?do=findComment&comment=864611).

```Bash
# add the following lines to /boot/config/go on your Unraid server.
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

Just as a PSA, if this list of commands is incorrect in `/boot/config/go` Unraid will fail to boot.

This will install Docker-Compose permanently on your server.

## Installing obico-server {#installing-obico}

obico-server can now be installed on your Unraid server the same way as the normal Linux method found on the [README.md]. However, I would recommend installing it in a directory other than the root home folder (`/root/`) as this data is not persistent between restarts. Either create a share specifically for obico-server or install it in an existing share, I recommend `/mnt/user/appdata/obico-server`. Here is the following command to do so.

```Bash
cd /mnt/user/appdata/
git clone -b release https://github.com/TheSpaghettiDetective/obico-server.git
# from the README
cd obico-server && docker-compose up -d
```

This will install obico-server to your Unraid server! To update obico-server, open up the terminal, change directory to the install directory, and run docker compose again.

```Bash
cd /mnt/user/appdata/obico-server # or where you install obico-server to
git pull
docker-compose up -d --force-recreate --build
```

## Configuring obico-server {#configuring-obico}
Navigate to port 3334/admin on your server.  For the following steps we will use `tower.local` as the server address with the root IP address as `192.168.1.10`.  Navigate to `tower.local:3334/admin` and log in with `root@example.com` and password `supersecret`

Go to Sites, click *example.com*, and change the Domain Name to your server IP address at port 3334, ex. `192.168.1.10:3334`.  Save the changes and exit out of the admin site.

Go to the non-admin site of the container by navigating to `tower.local:3334` and log in with the same credentials of `root@example.com`/`supersecret`.  Add a printer and install Obico on the Octoprint instance, setting the Server Address in OctoPrint to your server address:port like `http://192.168.1.10:3334`, then copy/paste the secret token in the correct location.

To get email notifications working, go back to the Unraid terminal and navigate to the obico-server installation directory with `cd /mnt/user/appdata/obico-server`.  Copy `dotenv.example` to `.env`, and open `.env` with `nano .env`.  You will need an [app-specific password](https://lmgtfy.app/?q=gmail+app+specific+password) for your email if you use 2-factor authentication.

Set the following:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=youremail@gmail.com
...
```

Rebuild the container (Note - if you are going to limit the CPU usage you can also change that now before rebuilding the container, see the below section) -

```bash
docker-compose up -d --force-recreate --build
```

## Issues with the Installation {#issues-with-the-installation}

Unlike most containers that you install to Unraid, containers installed with Docker-Compose are limited in what you can do with them through the GUI. You cannot update them, change their logo, description, or do anything except for stop and restart them through the GUI. When you update the containers, you must remove the old and outdated ones manually from the command line using `docker image rm`.

## Limit CPU Usage {#limit-cpu-usage}

By default obico-server will use all of the processing power available from your server just for approximately 1 second every 10 seconds for a typical quad-core or 6-core system.  You can use the following steps to limit obico-server to only using a certain amount of CPU usage.  This method doesn't actually constrain it to certain cores, but it sets the maximum processing power it can use overall.  So if you have a 4 core / 8 thread system, as far as docker-compose is concerned you have 8 "cpus".  Setting it to use 4 cpus will result in obico-server using 50% of your processing power for about 2 seconds, vs the original 100% power for 1 second.  If you have a 6-core/12-thread machine then `cpus: 6` would be using half of your machine power.

1. Use the Unraid GUI to Stop All running containers

2. Open a terminal and navigate to the obico-server install directory, then open the docker-compose.override.yml file:

  ```Bash
  cd /mnt/user/appdata/obico-server
  nano docker-compose.override.yml
  ```

3. Add `cpus: 4` to the services sections for `ml_api:` and `web:`

 ```Bash
services:
  ml_api:
    cpus: 4

  web:
    cpus: 4
```

4. Save the changed file.  Force the rebuild of the container with the following code:

  ```Bash
  docker-compose up -d --force-recreate  --build
  ```

5.  Navigate back to the Unraid GUI and Start All containers, you're all set!

## Use NVidia GPU

1. Use the Unraid GUI to Stop All running containers

2. Open a terminal and navigate to the obico-server install directory, then open the docker-compose.override.yml file:

  ```Bash
  cd /mnt/user/appdata/obico-server
  nano docker-compose.override.yml
  ```

3. Add `runtime: nvidia` to the services sections for `ml_api:`

```
version: '2.4'

services:
  ml_api:
    runtime: nvidia

```

4. Save the changed file.  Force the rebuild of the container with the following code:

  ```Bash
  docker-compose up -d --force-recreate  --build
  ```

5.  Navigate back to the Unraid GUI and Start All containers, you're all set!
