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

### Upgrading to the November 2026 release {#upgrading-to-the-november-2026-release}

This release fixes a number of security problems. A few of the fixes change how an existing server behaves. Read this before you upgrade.

#### What can break an existing server {#what-can-break-an-existing-server}

**1. A server behind a reverse proxy needs `NUM_TRUSTED_PROXIES`.** Set it in `.env` to the number of proxies in front of the server (for example `NUM_TRUSTED_PROXIES=1` for one NGINX, Traefik, Caddy or Cloudflare Tunnel), then restart. Earlier releases read each visitor's address from the `X-Forwarded-For` header without being told to. This release does so only when you say how many proxies add to that header. If you skip this step, every visitor looks like the proxy: they share one limit on sign-in attempts and wrong link codes, they see each other's unlinked printers when linking, and `ADMIN_IP_WHITELIST` is compared with the proxy's address. A server that visitors reach directly needs no change. See [the reverse proxy guide](advanced/reverse-proxy.md#4-tell-the-server-how-many-proxies-are-in-front-of-it).

**2. Everyone is signed out once if you never set `DJANGO_SECRET_KEY`.** Earlier releases fell back to a key that was written in the source code. This release generates a random key the first time it starts and keeps it in `backend/.django_secret_key`. Because the key changes, every browser and mobile app has to sign in again, once. The links to your timelapses, snapshots and G-Code files are re-signed when the server starts, so they keep working; a link that was copied out of the server before the upgrade (into a chat message, for example) stops working. Add `backend/.django_secret_key` to your backups. If you run the `web` and `tasks` containers without the shared `./backend` folder (Kubernetes, for example), set `DJANGO_SECRET_KEY` yourself so that both use the same key. If you already set `DJANGO_SECRET_KEY`, nothing changes. See [(Re-)generate `DJANGO_SECRET_KEY`](configure.md#re-generate-django_secret_key).

**3. Apps that sign in with OAuth reach less of the server.** An OAuth token now works only on the API for apps: printers, prints, G-Code files and folders, and the API version. Everything else, such as `users/me`, notification settings, tunnels and shared links, treats a request with only a token as signed out. The token must be sent as `Authorization: Bearer <token>`; a token in an `X-Api-Key` header no longer signs a request in. Only staff accounts can register an OAuth application under `/o/applications/`. As the server's admin you are staff. If a third-party app you use stops working after the upgrade, this is the likely cause; the app's developer can find the open endpoints in [the OAuth guide](../developer-guides/oauth-printer-management.md).

**4. Apps that send pictures to the predict API get refused more often.** `POST /api/v1/printers/{id}/predict/` now follows the same rules as the printer's own failure detection: detection must be on for a print that is running, the account must have AI Detection Hours left, and two pictures from the same printer must be at least 10 seconds apart. A refused picture is answered `403` with the reason, or `429` with `Retry-After`.

**5. `TUNNEL_DOMAIN`: leave it unset.** This new setting is used by the hosted service and is not supported on self-hosted servers yet. A server set up by [the tunnel guide](tunnel.md) gives each tunnel a port and does not need it. With it unset, tunnels work as before.

**6. `RELAY_HOST`: leave it unset unless you run your own TURN relay.** Video between a printer and a viewer on another network can go through a TURN relay. With `RELAY_HOST` set, the server hands printers, the web page and the app the relay's address with a credential that expires after 7 days, signed with `RELAY_SECRETS`. The relay must be [coturn](https://github.com/coturn/coturn) with `use-auth-secret` and the same secret. If `RELAY_HOST` is set without `RELAY_SECRETS`, the server refuses to start. Printers take the relay from the server from Obico for OctoPrint 2.7.5, and Obico for Klipper as installed from its `master` branch; older plugins do not use it. With `RELAY_HOST` unset, the server offers no relay, as before.

#### Printer plugins {#printer-plugins}

Every released version of Obico for OctoPrint and Obico for Klipper keeps working with this release, and you can upgrade the plugins before or after the server. We recommend Obico for OctoPrint 2.7.5 and Obico for Klipper 2.2.6 or later. From Obico for OctoPrint 2.7.4 and Obico for Klipper 2.2.6, automatic printer discovery is tied to the device that announced itself, so another device on the same network cannot pick up a printer's link code. Older plugins do not take part in that check.

#### Everything else in this release {#everything-else-in-this-release}

- **Printer link codes** are random from a secure source. After ten wrong 6-digit codes in an hour from one address, that address gets "too many requests" until the hour has passed.
- **Passwords.** New passwords need at least 8 characters, can't be a commonly used one or only digits, and can't be too close to the account's name or email address. The change-password and set-password pages say why a password was refused. Existing passwords keep working.
- **Sign-in and password reset** match only the email address that was typed.
- **Sign-up in the mobile app** asks for reCAPTCHA, as the website does, when `RECAPTCHA_SITE_KEY` is set. Without it, sign-up works as before.
- **Notifications.** A webhook or Apprise address that points at a private, loopback or other internal address (such as `192.168.x.x`, `100.64.x.x` or `localhost`) is refused when saved and again when sent, and a webhook does not follow redirects. Test messages are limited to 10 an hour per account.
- **Apps that send people to the tunnel authorization page.** After authorization the page returns only to an app's own address (such as `myapp://callback`) or to a page on your server. An address on another website is ignored.
- **Files.** Files are served only from inside the media folder. The `url` and thumbnail addresses of a G-Code file are written by the server; values sent by an API client are ignored. A printer reporting a downloaded file can set only a bare file name.
- **Text a printer sends**, such as the error message after a button press, is shown as text, and a printer event's links open only web pages.
- **Shared links** need a paid plan, which every account on a self-hosted server has. A shared link's page serves only the printer it was made for.
- Notification emails support one-click unsubscribe. Muting an alert after the print has ended no longer fails. Tunnel responses are compressed in a way OctoApp can read again.

## Backup database {#backup-database}

Just make a copy of `obico-server/backend/db.sqlite3`. Also keep a copy of `obico-server/backend/.django_secret_key` if that file exists.

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

