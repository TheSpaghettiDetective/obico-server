# Run Obico on unRAID

If video is your cup of tea, follow [this awesome video guide](https://www.youtube.com/watch?v=B2gjxL0MgEo) put together by Ricky at [SNR Tech Bytes](https://www.snrtechbytes.com/).Thank you Ricky!


## Install docker-compose {#install-docker-compose}

Since the original creation of this guide a great new tool to install Docker-Compose on unRAID has been released. It can be installed through the normal process of going to the Apps tab and doing a search for "Docker Compose Manager" and installing the plugin. The below instructions will still work if you'd like to do it manually, however, suggest using the Plug-In instead. Support can be found at the unRAID forums for the [Docker Compose Manager](https://forums.unraid.net/topic/114415-plugin-docker-compose-manager/).

#### Old process to install Docker-Compose: {#old-process-to-install-docker-compose}

To run Obico on unRAID, you first must install Docker-Compose on the server. This can be done following the usual instructions found on the [Docker-Compose Install Guide](https://docs.docker.com/compose/install/#install-compose-on-linux-systems).

```Bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

However, because unRAID boots from a USB to RAM, this installation will not be persistent. To make sure that Docker-Compose gets installed every time the server boots, follow the following steps from [this forum post](https://forums.unraid.net/topic/91436-is-docker-compose-available-on-unraid/?do=findComment&comment=864611).

```Bash
# add the following lines to /boot/config/go on your unRAID server.
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

Just as a PSA, if this list of commands is incorrect in `/boot/config/go` unRAID will fail to boot.

This will install Docker-Compose permanently on your server.

## Installing Obico {#installing-obico}

Obico can now be installed on your unRAID server the same way as the normal Linux method found on the [README.md]. However, I would recommend installing it in a directory other than the root home folder (`/root/`) as this data is not persistent between restarts. Either create a share specifically for Obico or install it in an existing share, I recommend `/mnt/user/appdata/Obico`. Here is the following command to do so.

```Bash
cd /mnt/user/appdata/
git clone -b release https://github.com/TheSpaghettiDetective/obico-server.git Obico
# from the README
cd Obico && docker-compose up -d
```

This will install Obico to your unRAID server! To update Obico, open up the terminal, change directory to the install directory, and run docker compose again.

```Bash
cd /mnt/user/appdata/Obico # or where you install Obico to
git pull
docker-compose up -d --force-recreate --build
```

## Configuring Obico {#configuring-obico}
Navigate to port 3334/admin on your server.  For the following steps we will use `tower.local` as the server address with the root IP address as `192.168.1.10`.  Navigate to `tower.local:3334/admin` and log in with `root@example.com` and password `supersecret`

Go to Sites, click *example.com*, and change the Domain Name to your server IP address at port 3334, ex. `192.168.1.10:3334`.  Save the changes and exit out of the admin site.

Go to the non-admin site of the container by navigating to `tower.local:3334` and log in with the same credentials of `root@example.com`/`supersecret`.  Add a printer and install Obico on the Octoprint instance, setting the Server Address in OctoPrint to your server address:port like `http://192.168.1.10:3334`, then copy/paste the secret token in the correct location.

To get email notifications working, go back to the Unraid terminal and navigate to the Obico installation directory with `cd /mnt/user/appdata/Obico`.  Open the docker-compose.yml file with `nano docker-compose.yml`.  You will need an [app-specific password](https://lmgtfy.app/?q=gmail+app+specific+password) for your email if you use 2-factor authentication.

Set the following:
```bash
EMAIL_HOST: 'smtp.gmail.com'     # -> such as 'smtp.gmail.com'
EMAIL_HOST_USER: 'youremail@gmail.com'
EMAIL_HOST_PASSWORD: 'abcdefghijklmnop'
...
DEFAULT_FROM_EMAIL:  'youremail@gmail.com'
```
Rebuild the container (Note - if you are going to limit the CPU usage you can also change that now before rebuilding the container, see the below section) -
```bash
docker-compose up -d --force-recreate --build
```

## Updating to Obico {#updating-to-obico}

Since Obico has been renamed to Obico, updates aren't pushed to the old Repository anymore, if you have previously installed Obico with the old repository, here are the steps to update.

```Bash
cd /mnt/user/appdata/TheSpaghettiDetective # or where you installed Obico to
git remote remove origin
git remote add origin https://github.com/TheSpaghettiDetective/obico-server.git
git fetch
git checkout release
docker-compose up --build -d
```

## Issues with the Installation {#issues-with-the-installation}

Unlike most containers that you install to unRAID, containers installed with Docker-Compose are limited in what you can do with them through the GUI. You cannot update them, change their logo, description, or do anything except for stop and restart them through the GUI. When you update the containers, you must remove the old and outdated ones manually from the command line using `docker image rm`.

## Limit CPU Usage {#limit-cpu-usage}
By default Obico will use all of the processing power available from your server just for approximately 1 second every 10 seconds for a typical quad-core or 6-core system.  You can use the following steps to limit Obico to only using a certain amount of CPU usage.  This method doesn't actually constrain it to certain cores, but it sets the maximum processing power it can use overall.  So if you have a 4 core / 8 thread system, as far as docker-compose is concerned you have 8 "cpus".  Setting it to use 4 cpus will result in Obico using 50% of your processing power for about 2 seconds, vs the original 100% power for 1 second.  If you have a 6-core/12-thread machine then `cpus: 6` would be using half of your machine power.
1. Use the Unraid GUI to Stop All running containers
2. Open a terminal and navigate to the Obico install directory, then open the docker-compose.yml file:
  ```Bash
  cd /mnt/user/appdata/Obico
  nano docker-compose.yml
  ```
3. Add `cpus: 4` at the bottom of the services sections for `ml_api:` and `web:` under the line that starts with `command: ` with the same indentation level as `command`.
 ```Bash
services:
  ml_api:
    hostname: ml_api
    restart: unless-stopped
    build:
      context: ml_api
    environment:
        DEBUG: 'True'
        FLASK_APP: 'server.py'
        #ML_API_TOKEN:
        #HAS_GPU: 'False'
    command: bash -c "gunicorn --bind 0.0.0.0:3333 --workers 2 wsgi"
    cpus: 4

  web:
    <<: *web-defaults
    hostname: web
    ports:
      - "3334:3334"
    depends_on:
      - ml_api
    command: sh -c "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver --no>
    cpus: 4
```
4. Save the changed file.  Force the rebuild of the container with the following code:
  ```Bash
  docker-compose up -d --force-recreate  --build
  ```
5.  Navigate back to the Unraid GUI and Start All containers, you're all set!
