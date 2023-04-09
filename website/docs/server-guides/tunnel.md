---
title: OctoPrint/Klipper tunnel
---

:::info
Because of the nature of OctoPrint/Klipper tunnel, there is no point to set it up without a reverse proxy. Please make sure you have the [reverse proxy set up and properly configured](./advanced/reverse-proxy.md) before proceeding to setting up the server for OctoPrint/Klipper tunnel.
:::

## Configure the Obico Server to serve OctoPrint tunnels {#configure-the-obico-server-to-serve-octoprint-tunnels}

### 1. Decide a range of ports to be used for the tunnels {#1-decide-a-range-of-ports-to-be-used-for-the-tunnels}

To make sure tunnels from different printers don't get mixed up, each tunnel uses a distinct port. The best practice is to allocate a range of ports that are unlikely to conflict with any other services running on the same host.

For instance, you can use port range 15853-15858, which can be allocated to up to 6 tunnels.

### 2. Add port range to `docker-compose.override.yml` {#2-add-port-range-to-docker-composeoverrideyml}

Create a file named `docker-compose.override.yml` (or add to it if you already have one) with a content similar to the follows. You need to adjust the port range if you are not using 15853-15873.

```yaml
version: "2.4"

services:
  web:
    environment:
      OCTOPRINT_TUNNEL_PORT_RANGE: "15853-15858"
    ports:
      - "15853:3334"
      - "15854:3334"
      - "15855:3334"
      - "15856:3334"
      - "15857:3334"
      - "15858:3334"
```

### 3. Restart the Obico Server {#3-restart-the-obico-server}

Run `docker compose stop && docker compose up -d`

## Configure the reverse proxy to forward _all the ports_ in the range {#configure-the-reverse-proxy-to-forward-all-the-ports-in-the-range}

All the ports in the range above needs to be forwarded by your reverse proxy. The details depend on the reverse proxy of your choice and is beyond the scope of this guide.
