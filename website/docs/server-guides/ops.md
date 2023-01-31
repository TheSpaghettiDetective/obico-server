---
title: Common tasks for operating self-hosted server
---

## Upgrade Obico Server {#upgrade-obico-server}

```
    cd obico-server
    git checkout release
    git pull
    docker compose up --build -d
```
*Note: if you are on linux you will have to run the last line as `sudo` (ex. `sudo docker...`)*

*Note: you need to use `docker-compose` instead of `docker compose` on older Docker versions*

## Backup database {#backup-database}

Just make a copy of `obico-server/backend/db.sqlite3`

## Access timelapses stored on your server {#access-timelapses-stored-on-your-server}

Although you can simply download the timelapses from either the web interface or the mobile app, it may be important to know exactly where the timelapses are stored on your local machine.

Path to timelapses:

`obico-server/backend/static_build/media/tsd-timelapses/private/`
