---
title: Configuration
---

## Basic server configuration

This is the bare minimum configuration required for the server to be reasonably useful.

### Django Site

#### Obtain server's IP address

This refers to the LAN IP address that has been given to the computer that the Obico server is running on. 
- If you are on Linux: Open the wifi settings and select "settings" for the network your device is currently connected to. Look for the IPv4 value. 
- If you are on Windows: Select "Properties" for the network your device is connected to, then look for the IPv4 value.
- If you are on Mac: Go to Settings > Network. You will find your IPv4 value below the wifi status.

The Obico Server needs to have an IP address that is accessible by OctoPrint or Klipper. It can be a private IP address (192.168.x.y, etc) but there needs to be a route between OctoPrint and the Obico Server. 

It is also reccomended that a static IP is set to avoid issues with chaning IP's. Please look up your WiFi routers guide on how to do this.

#### Creating and Obtaining your server's .local address

Similarly to how one can connect to octopi with octopi.local instead of an IP address, we can do the same for our Obico server.
:::caution
Doing this on a device that is already running software with similar functionality(ex. Homebridge) **may** cause issues. If a conflict does occur, it will not be fatal to either program or computer. This warning can mostly be ignored if this tool is new to you.
:::

- If you are on Linux, run `sudo apt install avahi-daemon`
- If you are on Windows, install [iTunes]([url](https://www.apple.com/itunes/)). This may sound odd, but this is the best and safest way to do this on Windows. The reason this must be done is because the latest version of the software we need(Bonjour) can only downloaded bundled with iTunes.
- If you are on Mac, you do not need to do anything. Mac already has this set up by default.

You can find your hostname by typing `hostname` into your terminal, regardless of OS.

You can now connect to your server with `your_host_name.local:3334`. Conveniently, your host name is not case sensitive. 

To reiterate, you can connect to your server with either your IPv4 address or .local address. If you choose to use a .local address, you may assume `your_server_ip` to be interchangeable with your .local address. You can use it not only as a URL, but also for SSH and any time you may need to connect directly to that device. 
#### Login as Django admin

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

*Note: If the browser complains "Can't connect to the server", wait for a couple more minutes. The web server container may still be starting up.*

2. Login with username `root@example.com`, password `supersecret`. Once logged in, you can optionally (but highly encouraged to) change the admin password using this link: `http://your_server_ip:3334/admin/app/user/1/password/`.

#### Configure Django site

1. In the same browser window, go to the address `http://your_server_ip:3334/admin/sites/site/1/change/`. Change "Domain name" to `your_server_ip:3334`. No "http://", "https://" prefix or trailing "/", otherwise it will NOT work. *Note: Deleting the original site and adding a new one won't work, thanks to the quirkiness of Django site.*

2. Click "Save". Yes it's correct that Django is not as smart as most people think. ;)

![Site configuration](/img/server-guides/site_config.png)

*Note: If you are using reverse proxy, "Domain name" needs to be set to `reverse_proxy_ip:reverse_proxy_port`. See [using a reverse proxy](advanced/reverse-proxy.md) for details.*

### Email (SMTP)

The following is using gmail as an example. Other web mail services may vary slightly, such as EMAIL_PORT

1. In `obico-server` directory, make a copy of `dotenv.example` and rename the copy as `.env`.

2. Open `.env` using your favorite editor.

3. Find the following lines, and set them to the correct values of your email account:

```
EMAIL_HOST=your_email_host_here
# Such as your email address for a Outlook account. Note: Gmail has disabled SMTP support and hence won't work

EMAIL_HOST_USER=your_email_user_here
# Your email account password

EMAIL_HOST_PASSWORD=your_email_password_here

EMAIL_PORT=587
# Check with your email provider to make sure.

EMAIL_USE_TLS=True
# Set it to 'False' if your email provider doesn't use TLS, which is uncommon
```

4. Restart the server `docker-compose up --build -d`.

If you run into issues with Email server settings, please follow this [Email server trouble-shooting guide](advanced/email_guide.md).


## Advanced server configuration

Ready for some advanced server chops? Feel free to dive into the [advanced server stuff](advanced/index.md).

### If you don't need to add a new environment variable

TBD

### If you need to add a new environment variable

TBD
