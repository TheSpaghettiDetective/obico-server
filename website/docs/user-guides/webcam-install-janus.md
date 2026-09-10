---
title: Janus Not Installed
---

If you got this error message, it means Janus is not installed on your system.

![Janus Not Found](/img/user-guides/helpdocs/janus-not-found-warning.png)

## What is Janus? {#what-is-janus}

Janus is a software that allows you to stream high-FPS realtime video from your webcam to the Obico app.

In most cases, you don't need to install Janus separately, because Obico Server will automatically install it for you.

However, there are some cases where the automatic installation fails, you will need to install it manually.

## How to install Janus manually {#how-to-install-janus-manually}

Depending on your operating system, you will need to install Janus with different methods.

### On Debian-based systems (like Raspberry Pi OS or Ubuntu) {#on-debian-based-systems-like-raspberry-pi-os-or-ubuntu}

You can install Janus with the following command:

```bash
sudo apt-get install -y janus
```

:::caution Debian 13 "Trixie" has no `janus` package
The command above will fail with "Unable to locate package janus" on Debian 13 (Trixie), including Armbian images based on it. The package is available in Debian 12 (Bookworm) and in `forky`/`sid`, but it is missing from `trixie`, `trixie-updates`, and `trixie-backports`.

On Trixie you have to build Janus from source — and it has to be built with data channel and WebSockets support, then registered with `dpkg`, or Obico still won't find it. See [Fixing the Obico Webcam Feed on Debian 13 (Trixie)](/blog/install-janus-debian-trixie-obico/) for a script that does this and verifies each step.
:::

### On Fedora {#on-fedora}

You can install Janus with the following command:

```bash
sudo dnf install -y janus
```
