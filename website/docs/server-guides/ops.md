---
title: Common tasks for operating self-hosted server
---

## Upgrade Obico Server {#upgrade-obico-server}

```
    cd obico-server
    git checkout release
    git pull
    docker compose up -d
```
*Note: if you are on linux you _may_ need to run the last line as `sudo` (ex. `sudo docker...`)*

*Note: on an NVIDIA Jetson, run the last line as `docker compose -f docker-compose.yml -f docker-compose.jetson.yml up -d` — the default compose file pulls amd64 images that a Jetson cannot run.*

*Note: the server now runs prebuilt images pulled from the registry, so no local rebuild happens during an upgrade. If you build from source (`docker-compose.build.yml`), add `--build` to the last line.*

*Note: right after a new release is published there is a short window (until its build pipeline finishes) where `git pull` already delivers the new code but the image pin still references the previous build. If an upgrade misbehaves immediately after a release, wait for the build to finish, then run `git pull && docker compose up -d` again.*

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

