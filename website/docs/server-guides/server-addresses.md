---
title: Obtain Obico Server Address
---

This guide provides a few commons ways to obtain the address of your Obico Server. It is not intended as a comprehensive or detailed document for how your Obico Server can be addressed.

## Obtain server's LAN IP address {#obtain-servers-ip-address}

This refers to the LAN IP address of the computer that the Obico Server is running on.

- If you are on Linux: Open the wifi settings and select "settings" for the network your device is currently connected to. Look for the IPv4 value.
- If you are on Windows: Select "Properties" for the network your device is connected to, then look for the IPv4 value.
- If you are on Mac: Go to Settings > Network. You will find your IPv4 value below the wifi status.

The Obico Server needs to have an IP address that is accessible by OctoPrint or Klipper. It can be a private IP address (192.168.x.y, etc) but there needs to be a route between OctoPrint and the Obico Server.

It is also recommended that a static IP is set to avoid issues with changing IP's. Please look up your WiFi routers guide on how to do this.

## Creating and Obtaining your server's mDNS (.local) address {#creating-and-obtaining-your-servers-local-address}

Similarly to how one can connect to octopi with octopi.local instead of an IP address, we can do the same for our Obico Server.

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