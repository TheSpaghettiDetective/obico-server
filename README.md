# TheSpaghettiDetective

This repo is everything you need to run a server for [The Spaghetti Detective](https://thespaghettidetective.com), the coolest, AI-based solution for 3D printer remote management and monitoring.

# Install and run the server

## Prerequisites

The Spaghetti Detective server requires:

- Docker and Docker-compose. But you don't have to understand how Docker or Docker-compose works.
    - Install Docker ([Windows](https://docs.docker.com/docker-for-windows/install/), [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Mac](https://docs.docker.com/docker-for-mac/install/)).
    - [Install Docker-compose](https://docs.docker.com/compose/install/).

- git-lfs. This is because the model itself is 100+MB and therefore can't be directly checked into git.
    - [Install git-lfs](https://github.com/git-lfs/git-lfs/wiki/Installation).

## Get the code and start the server.

1. Get the code:

    git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git

2. Run it! Do **EITHER** one of these:
    - If you are on Linux: `cd TheSpaghettiDetective && sudo docker-compose up -d`
    - If you are on Mac: `cd TheSpaghettiDetective && docker-compose up -d`
    - If you are on Windows: ???

3. Go grab a coffee. Step 2 would take up to 30 minutes. BTW, we need help to shorten this process. Let us know if you can pitch in.

4. There is no step 4. This is how easy it is to get The Spaghetti Detective up and running (thanks to Docker and Docker-compose).


# Basic server configuration

These are the bare minimum configuration required for the server to be functional.

## Obtain server's IP address

The Spaghetti Detective server needs to have an IP address that is accessible by OctoPrint. It can be an private IP address (192.168.x.y, etc) but there needs to be a route between OctoPrint and The Spaghetti Detective server.

## Port/Firewall

The Spaghetti Detective server listens on port 3334 (will be configurable in later version). Please make sure this port is not blocked from OctoPrint.

You can set up a reverse-proxy, such as nginx, in front of The Spaghetti Detective server, so that it's exposed on a different port. In this case, please use whichever port you choose to expose in the steps below. For simplicity
sake, this document assumes the server port is 3334.

## Login as Django admin

1. Open Django admin page at `http://your_serer_ip:3334/admin/`

2. Login with username `root@example.com`, password `supersecret`. Once logged in, you can optionally (but highly encouraged to) change admin password using this link: `http://your_server_ip:3334/admin/app/user/1/password/`.

## Configure Django site

1. On Django admin page, click "Sites", and click the only entry "example.com" to bring up the site you need to configure. Change "Domain name" to `your_server_ip:3334`. No "http://", "https://" prefix or trailing "/", otherwise it will NOT work.

2. Click "Save". Yes it's correct that Django is not as smart as most people think. ;)

![Site configuration](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/site_config.png)

# Configure The Spagetti Detective OctoPrint Plugin to use your own server

On The Spaghetti Detective plugin settings page:

1. Check the box "I have my own TSD server. Don't check this unless you know what you are doing."

2. Enter `http://your_serer_ip:3334/`. This time you need to enter both "http://" and the trailing "/". I know it's confusing but...

3. Click "Save". OctoPrint isn't necessarily smarter than Django after all.

![Site configuration](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/plugin_config.png)


# Advanced server configuraion

## Enable social login (TBD)

## Change email server to be one other than `sendmail` on localhost (TBD)


# Operating and maintaining The Spaghetti Detective server

## Upgrade server

    git pull
    sudo docker-compose up --build -d

## Backup database

Just make a copy of `TheSpaghettiDetective/web/db.sqlite`

# Difficulties at getting The Spaghetti Detective server up and running? [Open an issue](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/new).
