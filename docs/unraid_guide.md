# Run TSD on unRAID

If video is your cup of tea, follow [this awesome video guide](https://www.youtube.com/watch?v=B2gjxL0MgEo) put together by [u/rickyh7](https://www.reddit.com/user/rickyh7/).Thank you u/rickyh7 !


## Install docker-compose

To run TSD on unRAID, you first must install Docker-Compose on the server. This can be done following the usual instructions found on the [Docker-Compose Install Guide](https://docs.docker.com/compose/install/#install-compose-on-linux-systems).

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

## Installing TSD

TSD can now be installed on your unRAID server the same way as the normal Linux method found on the [README.md]. However, I would recommend installing it in a directory other than the root home folder (`/root/`) as this data is not persistent between restarts. Either create a share specifically for TSD or install it in an existing share, I recommend `/mnt/user/appdata/TheSpaghettiDetective`. Here is the following command to do so.

```Bash
cd /mnt/user/appdata/
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
# from the README
cd TheSpaghettiDetective && docker-compose up -d
```

This will install TSD to your unRAID server! To update TSD, open up the terminal, change directory to the install directory, and run docker compose again.

```Bash
cd /mnt/user/appdata/TheSpaghettiDetective # or where you install TSD to
git pull origin master
docker-compose up -d --force-recreate --build
```

## Issues with the Installation

Unlike most containers that you install to unRAID, containers installed with Docker-Compose are limited in what you can do with them through the GUI. You cannot update them, change their logo, description, or do anything except for stop and restart them through the GUI. When you update the containers, you must remove the old and outdated ones manually from the command line using `docker image rm`.

