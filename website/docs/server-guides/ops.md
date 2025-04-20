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
*Note: if you are on linux you _may_ need to run the last line as `sudo` (ex. `sudo docker...`)*

*Note: you need to use `docker-compose` instead of `docker compose` on older Docker versions*

## Backup database {#backup-database}

Just make a copy of `obico-server/backend/db.sqlite3`

## Access timelapses stored on your server {#access-timelapses-stored-on-your-server}

Although you can simply download the timelapses from either the web interface or the mobile app, it may be important to know exactly where the timelapses are stored on your local machine.

Path to timelapses:

`obico-server/backend/static_build/media/tsd-timelapses/private/`

## Prune old images {#prune-old-images}

As you upgrade the Obico Server containers, old (now unused) versions of these containers will be left behind.  To remove these old images, one can run the following:

```
docker image prune
```

*Note: if you are on linux you _may_ need to run the last line as `sudo` (ex. `sudo docker...`)*

## Customize healthchecks {#customize-healthchecks}

Using healthchecks in `docker-compose.yaml` to monitor and ensure the reliability of self-hosted services running in Docker Compose is a great way to maintain uptime and quickly react to failures.

Short explanation of healthcheck parameters :

- `test` : The command to run to check the health inside the container (you shouldn't have to change it).
- `start_period` : The time to wait after the container starts before health checks begin.
- `interval` : The time to wait between health checks.
- `timeout` : The time to wait before considering the health check to have failed
- `retries` : The number of consecutive failures needed to consider a container as unhealthly

Feel free to customize them as you wish.

