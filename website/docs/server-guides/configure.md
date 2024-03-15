---
title: Configuration
---

## Basic server configuration {#basic-server-configuration}

This is the bare minimum configuration required for the server to be reasonably useful.

### Django Site {#django-site}

#### Obtain server's IP address {#obtain-servers-ip-address}

This refers to the LAN IP address that has been given to the computer that the Obico server is running on.
- If you are on Linux: Open the wifi settings and select "settings" for the network your device is currently connected to. Look for the IPv4 value.
- If you are on Windows: Select "Properties" for the network your device is connected to, then look for the IPv4 value.
- If you are on Mac: Go to Settings > Network. You will find your IPv4 value below the wifi status.

The Obico Server needs to have an IP address that is accessible by OctoPrint or Klipper. It can be a private IP address (192.168.x.y, etc) but there needs to be a route between OctoPrint and the Obico Server.

It is also recommended that a static IP is set to avoid issues with changing IP's. Please look up your WiFi routers guide on how to do this.

#### Creating and Obtaining your server's .local address {#creating-and-obtaining-your-servers-local-address}

Similarly to how one can connect to octopi with octopi.local instead of an IP address, we can do the same for our Obico server.
:::caution
Doing this on a device that is already running software with similar functionality(ex. Homebridge) **may** cause issues. If a conflict does occur, it will not be fatal to either program or computer. This warning can mostly be ignored if this tool is new to you.
:::

- If you are on Windows, install [iTunes](https://www.apple.com/itunes/). This may sound odd, but this is the best and safest way to do this on Windows. The reason this must be done is because the latest version of the software we need(Bonjour) can only downloaded bundled with iTunes.
- If you are on Mac, you do not need to do anything. Mac already has this set up by default.
- If you are on Linux, most distros come with `avahi-daemon` installed(ubuntu, debian, arch, redhat). Instructions on installation/update for `avahi-daemon` for your distro can be found online.
  - To enable Avahi, run `sudo systemctl enable avahi-daemon && sudo systemctl start avahi-daemon`. You are now done.
  - Although optional, we recommend you change some settings in your config file.
    - Located in `/etc/avahi/avahi-daemon.conf`, uncomment(if needed, done by removing the `#`) and set `publish-addresses`, `publish-hinfo`, `publish-workstation`, `publish-domain` all equal to `yes`. Do **not** include spaces before and after the equal sign
    - More optionally, you can change the hostname of the service by uncommenting and setting `hostname` to whatever you would like.
    - you can now restart avahi by running `sudo systemctl restart avahi-daemon`
    - More information on this can be found in the [docs](https://manpages.ubuntu.com/manpages/trusty/man5/avahi-daemon.conf.5.html).

You can find your hostname by typing `hostname` into your terminal, regardless of OS.

You can now connect to your server with `your_host_name.local:3334`. Conveniently, your host name is not case sensitive.

To reiterate, you can connect to your server with either `your_server_ip:3334` or `your_host_name.local:3334`. If you choose to use a .local address, you may assume `your_server_ip` to be interchangeable with your .local address. You can use it not only as a URL, but also for SSH and as a general replacement for the ip address.
#### Login as Django admin {#login-as-django-admin}

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

*Note: If the browser complains "Can't connect to the server", wait for a couple more minutes. The web server container may still be starting up.*

2. Login with username `root@example.com`, password `supersecret`. Once logged in, you can optionally (but highly encouraged to) change the admin password using this link: `http://your_server_ip:3334/admin/app/user/1/password/`.

#### Configure Django site {#configure-django-site}

1. In the same browser window, go to the address `http://your_server_ip:3334/admin/sites/site/1/change/`. Change "Domain name" to `your_server_ip:3334`. No "http://", "https://" prefix or trailing "/", otherwise it will NOT work. *Note: Deleting the original site and adding a new one won't work, thanks to the quirkiness of Django site.*

2. Click "Save". Yes it's correct that Django is not as smart as most people think. ;)

![Site configuration](/img/server-guides/site_config.png)

*Note: If you are using reverse proxy, "Domain name" needs to be set to `reverse_proxy_ip:reverse_proxy_port`. See [using a reverse proxy](advanced/reverse-proxy.md) for details.*

### Email (SMTP) {#email-smtp}

The following is using gmail as an example. Other web mail services may vary slightly, such as EMAIL_PORT

1. In `obico-server` directory, make a copy of `dotenv.example` and rename the copy as `.env`.

2. Open `.env` using your favorite editor.

3. Find the following lines, and set them to the correct values of your email account (make sure to remove the pound "#" symbols):

```text
EMAIL_HOST=

EMAIL_HOST_USER=
# Such as your email address for a Gmail account

EMAIL_HOST_PASSWORD=
# Your email account password

EMAIL_PORT=587
# Check with your email provider to make sure.

EMAIL_USE_TLS=True
# Set it to False if your email provider doesn't use TLS, which is uncommon
```

4. Restart the server `docker compose up --build -d`.

You can follow [this guide](advanced/gmail_smtp_setup_guide.md) if you want to use a Gmail account to send emails.

If you run into issues with Email server settings, please follow this [Email server trouble-shooting guide](advanced/email_guide.md).
*Note: Make sure to to remove the # or else it will not work.

### (Re-)generate `DJANGO_SECRET_KEY` {#re-generate-django_secret_key}

This step is optional. But you are highly recommended to generate `DJANGO_SECRET_KEY` and rotate (re-generate) it periodically, especially if you have your Obico Server exposed to the Internet via reverse proxy.

:::caution
If this step is omitted, the Obico Server will use the default value, which is not recommended unless your intention is just to quickly spin up an temporary Obico Server for evaluation or testing.
:::

:::caution
If you are upgrading the Obico Server from a version before October 20th, 2023, you need to go through these steps. Otherwise, all of your previous prints and G-Code files will be unusable.
:::

1. Randomly generate the next `DJANGO_SECRET_KEY`:

```
docker compose exec web ./manage.py gen_site_secret
```

2. Copy the `DJANGO_SECRET_KEY=xxx` line in the output of the previous command into `.env`

3. Restart the Obico Server:

```
docker compose stop && docker compose up -d
```

4. Re-sign all media URL. This step is important, otherwise all of your previous prints and G-Code files will be unusable.

```
docker compose exec web ./manage.py resign_media_urls
```


## What's next? {#whats-next}

### Advanced server configuration {#advanced-server-configuration}

Ready for some advanced server chops? Feel free to dive into the [advanced server stuff](advanced/index.md).

### Keep your server up to date {#keep-your-server-up-to-date}

The Obico Server is designed to be backward compatible, not forward compatible. This means the server can work with the old client versions released in the past, but not the client versions that will be released in the future.

The clients here include the Obico mobile app, Obico for OctoPrint and Obico for Klipper

:::caution

Always [upgrade your self-hosted Obico Server](ops.md/#upgrade-obico-server) before you upgrade the Obico mobile app, Obico for OctoPrint or Obico for Klipper to a new version.

:::
