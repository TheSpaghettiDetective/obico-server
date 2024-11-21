---
title: Installation
---

:::info

This is a general guide to install the Obico Server. For platform-specific guides:

- [Obico installation guide for Windows Server](platform-specific/server_2019.md)
- [Obico installation guide for NVIDIA Jetson Nano](platform-specific/jetson_guide.md)
- [Obico installation guide for Unraid](platform-specific/unraid_guide.md)

:::

:::caution
Guides not directly maintained by the Obico Team and Contributors may be outdated, and should be used at user discretion. Always cross-check commands and instructions used with those located on the [official doc site](https://www.obico.io/docs/server-guides/).
:::

## Hardware Requirements {#hardware-requirements}

The Obico Server only requires a computer to run. Even old PCs (within the previous 10 years) will do just fine. A NVidia GPU is optional but can vastly reduce the power consumption and beef up the number of printers the server can handle.

[More details about the hardware requirements for the Obico Server](hardware-requirements.md).

:::caution

Don't try to install the Obico Server on a Raspberry Pi. Pi's CPU is too weak to run the Machine Learning failure-detection model.

:::

## 1. Install required softwares {#1-install-required-softwares}

The following software is required before you start installing the server:

- Docker and Docker-compose. But you don't have to understand how Docker or Docker-compose works.
    - Install Docker ([Windows](https://docs.docker.com/docker-for-windows/install/), [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Fedora](https://docs.docker.com/engine/install/fedora/), [CentOS](https://docs.docker.com/engine/install/centos/), [Mac](https://docs.docker.com/docker-for-mac/install/)). **Important:** If your server has an old Docker version, please follow the instructions in these links to upgrade to the latest version, otherwise you may run into all kinds of weird problems.
    - [Install Docker-compose](https://docs.docker.com/compose/install/). You need Docker-compose V2.0 or higher.
- git ([how to install](https://git-scm.com/downloads)).


## 2. Get the code and start the server. {#2-get-the-code-and-start-the-server}

1. Get the code:

```
git clone -b release https://github.com/TheSpaghettiDetective/obico-server.git
```

2. Run it! Do **either** one of these based on what OS you are using:
    - If you are on Linux: `cd obico-server && sudo docker compose up -d`
    - If you are on Mac: `cd obico-server && docker compose up -d`
    - If you are on Windows: `cd obico-server; docker compose up -d`

:::tip
You need to use `docker-compose` instead of `docker compose` on older Docker versions.
:::

:::tip
docker-compose.yaml use [healthchecks](https://docs.docker.com/reference/compose-file/services/#healthcheck). If you want to customize it, please go to [Common tasks for operating self-hosted server](https://www.obico.io/docs/server-guides/ops/#customize-healthchecks).
:::

3. Go grab a coffee. Step 2 will take 15-30 minutes.

4. If the Obico Server is running on `localhost`, there will be no step 4. If it is running on a different host, such as a VM in the cloud, go ahead to [configure the Django site](configure.md#django-site).

## 3. Test the server {#3-test-the-server}

Open [http://localhost:3334](http://localhost:3334) on the same computer. If you see this page, then congratulations - your self-hosted Obico Server is now up and running!

![](/img/server-guides/login-page.png)

## 4. Configure the server {#4-configure-the-server}

Your Obico Server will [need some basic configurations](configure.md) to work correctly with OctoPrint or Klipper, or to send emails and other notifications.
