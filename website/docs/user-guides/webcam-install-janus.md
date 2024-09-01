---
title: Janus Not Found
---

If you got this error message, it means Janus is not installed on your system.

![Janus Not Found](/img/user-guides/helpdocs/janus-not-found-warning.png)

## What is Janus?

Janus is a software that allows you to stream high-FPS realtime video from your webcam to the Obico app.

In most cases, you don't need to install Janus separately, because Obico Server will automatically install it for you.

However, there are some cases where the automatic installation fails, you will need to install it manually.

## How to install Janus manually

Depending on your operating system, you will need to install Janus with different methods.

### On Debian-based systems (like Raspberry Pi OS or Ubuntu)

You can install Janus with the following command:

```bash
sudo apt-get install -y janus
```

### On Fedora

You can install Janus with the following command:

```bash
sudo dnf install -y janus
```
