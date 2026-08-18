---
title: Set up a TURN server for webcam streaming
description: Get WebRTC webcam streaming working from mobile networks.
---

:::tip Do you need this?
Only if your server is reachable from the internet and you want webcam streaming from networks other than your own, such as your phone on mobile data. If you use Obico on your LAN, or over a VPN or tailnet, WebRTC connects directly and a TURN server changes nothing. In that case go through [Why doesn't the webcam streaming work for my self-hosted server?](../faqs.md#why-doesnt-the-webcam-streaming-work-for-my-self-hosted-server) first.
:::

Webcam streaming uses WebRTC, which tries to connect the browser directly to the printer. That doesn't work from many networks, mobile networks in particular. WebRTC then needs a TURN server to relay the video. Without one the video pane spins forever while everything else works.

The Obico Cloud runs its own TURN server. For a self-hosted server you run your own and point Obico Server at it. The server passes the TURN config to the web page and to the printer agents, so the printers need no configuration.

:::info
Agents read the TURN config at startup. Restart Obico for Klipper / Obico for OctoPrint after changing it. Older agents ignore it.
:::

## 1. Run a TURN server {#run-a-turn-server}

Any TURN server works. This guide uses [coturn](https://github.com/coturn/coturn). It has to be reachable from the internet, so it needs a public IP (or forwarded ports) and a DNS name.

It also has to be reachable from the printer, with the same `TURN_SERVER` value. If the TURN server sits inside your LAN, a public hostname only resolves from inside if your router supports hairpin NAT. Setting `TURN_SERVER` to the LAN IP works too: the printer's relay alone is usually enough for streaming, and browsers skip a TURN server they can't reach.

:::danger
A TURN server relays traffic for anyone with valid credentials. Apply the [hardening](#harden-the-turn-server) below before exposing it. Without `denied-peer-ip`, a leaked credential is a way into your LAN.
:::

Pick one credential mode.

### Recommended: time-limited credentials {#time-limited-credentials}

Obico Server and the TURN server share a secret. Obico Server issues short-lived credentials from it: one day for browsers, one year for agents (both configurable). Nothing permanent reaches a browser, so a credential leaked from a web page is dead the next day.

`turnserver.conf`:

```
listening-port=3478
realm=turn.example.com
use-auth-secret
static-auth-secret=<openssl rand -hex 32>
```

This is the "TURN REST API" scheme. coturn, eturnal, Pion and most hosted TURN services support it.

### Alternative: static credentials {#static-credentials}

One fixed username and password for every browser and agent. Use this only if your TURN server can't do time-limited credentials. Anyone who can open a printer page, including anyone with a share link, can read them.

```
listening-port=3478
realm=turn.example.com
lt-cred-mech
user=obico:<long random password>
```

### Harden the TURN server {#harden-the-turn-server}

Add these in either mode:

```
# Never relay to private networks. Do NOT deny 100.64.0.0/10 (CGNAT): phones
# on mobile data often live there, and denying it blocks exactly those viewers.
no-multicast-peers
denied-peer-ip=0.0.0.0-0.255.255.255
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=127.0.0.0-127.255.255.255
denied-peer-ip=169.254.0.0-169.254.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255
denied-peer-ip=::1
denied-peer-ip=fc00::-fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
denied-peer-ip=fe80::-febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff

# Limit what one credential can do
total-quota=100
user-quota=10
max-bps=3000000
stale-nonce=600
```

Open only the ports you use (3478 udp/tcp by default, plus the relay range if you set `min-port`/`max-port`).

## 2. Configure Obico Server {#configure-obico-server}

TURN is enabled by setting `TURN_SERVER`. Unset, the server behaves as before and the other `TURN_*` settings do nothing.

Add to `.env` (see [Configure Obico Server using `.env`](index.md#configure-obico-server-using-env)) and restart the server.

Time-limited credentials:

```
TURN_SERVER=turn.example.com
TURN_PORT=3478
TURN_TRANSPORTS=udp,tcp
TURN_SECRET=<same as static-auth-secret>
```

Static credentials:

```
TURN_SERVER=turn.example.com
TURN_PORT=3478
TURN_TRANSPORTS=udp,tcp
TURN_USERNAME=obico
TURN_CREDENTIAL=<same as in turnserver.conf>
```

`TURN_TRANSPORTS` is what your TURN server listens on. `TURN_WEB_CREDENTIAL_TTL` (default 86400) and `TURN_AGENT_CREDENTIAL_TTL` (default 31536000) are the credential lifetimes in seconds. With `TURN_SERVER` set, the server won't start unless exactly one credential mode is configured.

## 3. Verify {#verify}

1. Restart the agent. Its log shows which TURN server it is using.
2. On a phone with Wi-Fi off, open `chrome://webrtc-internals` in one tab and a printer page in another. When the video plays, the selected candidate pair should have a remote candidate of type `relay`.

If it doesn't play, check the TURN server log for auth errors (wrong secret or password) and that the TURN ports are reachable from the internet.
