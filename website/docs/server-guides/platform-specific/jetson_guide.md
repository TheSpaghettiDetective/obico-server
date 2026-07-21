---
title: Run Obico Server on NVIDIA Jetson Nano
---


*If you follow this guide and run into problems, please seek help at: https://obico.io/discord*

## Prerequisites {#prerequisites}

### Hardware requirements {#hardware-requirements}

Obico private server can only run on Jetson Nano 4GB model. The 2GB model doesn't have enough memory to run both the program and load the AI model in the memory.

### Software requirements {#software-requirements}

**Important:** Before you flash new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a different OS on your sd card, you will have to replace it with this one. Slow download of the software from NVIDIA is normal.
- [Flashing Software](https://www.balena.io/etcher/)
- [SD Card Formatter](https://www.sdcard.org/downloads/formatter/)

### Email delivery {#email-delivery}

You will also need an email account that has SMTP access enabled. For a gmail account, this is [how you enable SMTP access](https://support.google.com/accounts/answer/6010255?hl=en). Other web mail such as Yahoo
should also work but we haven't tried them.

## Get the code and start the server. {#get-the-code-and-start-the-server}

1. Get the code:

```bash
git clone -b release https://github.com/TheSpaghettiDetective/obico-server.git
```

2. Run it!

```bash
cd obico-server
./scripts/install_on_jetson.sh
```

3. Go grab a coffee. Step 2 will take a few minutes while the prebuilt images are downloaded.

4. There is no step 4. This is how easy it is to get the Obico Server up and running (thanks to Docker and Docker-compose).

## Upgrading {#upgrading}

The default upgrade command from the [operating guide](../ops.md) pulls amd64 images that a Jetson cannot run — on a Jetson, upgrade with the Jetson compose file instead:

```bash
cd obico-server
git pull
sudo docker compose -f docker-compose.yml -f docker-compose.jetson.yml up -d
```

*On older JetPack releases, where the install script set up docker-compose v1, use `docker-compose` (with a dash) instead of `docker compose`.*

## If the prebuilt image is not available {#if-the-prebuilt-image-is-not-available}

The Jetson inference image is published on a best-effort basis. If the pull fails (for example, right after a new release before its Jetson build has finished, if a Jetson build failed, or if the GHCR package has not been made public), you can build on the device instead, exactly like older versions of the server did: open `docker-compose.jetson.yml` and replace the `image:` line with

```yaml
    image: obico-ml-api-jetson:local
    build:
      context: ml_api
```

(the `obico-ml-api-jetson:local` name matters — without it the on-device build would be tagged with the name of a published image), then re-run the same `docker compose -f docker-compose.yml -f docker-compose.jetson.yml up -d` command with `--build` appended.

## Continue to [server configuration the main documentation](../../configure) {#continue-to-server-configuration-the-main-documentation}

*Thanks to the work of Raymond, LyricPants, and others for their contribution!*
