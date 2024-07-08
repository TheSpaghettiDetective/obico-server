---
id: config
title: Configurations
---

Following Klipper toolchain's convention, the configuration file for **Obico for Klipper** is typically located at `~/printer_data/config/moonraker-obico.cfg`

You can SSH to your printer or Raspberry Pi and use editor such as `nano` to make changes to the configuration file.

Alternatively, you can use the web interface to make changes if you are using Mainsail or Fluidd.

![](/img/user-guides/helpdocs/open-moonraker-obico-cfg.png)

:::caution
You need to restart the printer or Raspberry Pi for any change to take effect.
:::

The ways to restart the printer or Raspberry Pi are slightly different between Mainsail and Fluidd. But the button is usually located at the top-right corner of the screen.

![](/img/user-guides/helpdocs/restart-printer-pi.png)

## An example of the configuration file {#an-example-of-the-configuration-file}

```
[server]
url = https://app.obico.io
# auth_token: <let the link command set this, see more in readme>
# sentry_opt: out or in

[moonraker]
host = 127.0.0.1
port = 7125
# api_key = <grab one or set trusted hosts in moonraker>

[webcam]
disable_video_streaming = False

# CAUTION: Don't set this section unless you know what you are doing
#   In most cases webcam configuration will be automatically retrieved from moonraker
#
# snapshot_url = http://127.0.0.1:8080/?action=snapshot
# stream_url = http://127.0.0.1:8080/?action=stream
# target_fps = 25
# flip_h = False
# flip_v = False
# rotation = 0
# aspect_ratio_169 = False

[logging]
path = /home/pi/printer_data/logs/moonraker-obico.log
level = INFO

[tunnel]
# CAUTION: Don't modify the settings below unless you know what you are doing
# dest_host = 127.0.0.1
# dest_port = 80
# dest_is_ssl = False

```

## `[server]` section {#server-section}

The configuration for connecting to the Obico Server.

### `url` {#url}

The URL for the Obico Server. Such as "https://app.obico.io".

### `auth_token` {#auth_token}

The authentication token to authenticate Obico for Klipper client to the Obico Server. This is typically obtained by the `install.sh` from the server during the linking process. Don't directly set it.

## `[moonraker]` section {#moonraker-section}

### `host` {#host}

Moonraker host. Usually it's "127.0.0.1", namely the same host as **Obico for Klipper**.

### `port` {#port}

The port Moonraker is listening on. The default port for Moonraker is 7125 but can be a different one, which is very typical on a system that runs multiple Moonraker instances.

## `[webcam]` section {#webcam-section}

In the majority of the cases, you will only need the minimum `[webcam]` section as follows:

```
[webcam]
disable_video_streaming = False
```

If you have a special webcam setup, or have run into issues with your webcam in Obico, check out the detailed [webcam configuration guide](webcam.md).

## `[logging]` section {#logging-section}

### `path` {#path}

The path to the log file. Will be automatically rotated at 5MB size.

### `level` {#level}

Default to `INFO`. Set to `DEBUG` to see _a lot_ more details in the logs

## `[tunnel]` section {#tunnel-section}

The configuration specifically for Klipper Tunnel. Most of the time you should just leave them as default.

### `dest_host` {#dest_host}

Default to `127.0.0.1`. The hostname or IP address that you want to the tunnel request to be sent to. It is typically the same as the hostname/IP you enter in the browser to use Mainsail/Fluidd. For example, `mainsailos.local`, or `192.168.0.32`. Do NOT include "http://" or the port number here.

### `dest_port` {#dest_port}

Default to `80`. The port that you want to the tunnel request to be sent to. This is typically 80 (default).

### `dest_is_ssl` {#dest_is_ssl}

Default to `False`. You almost should never set this to `True` unless you do know that your Klipper only be accessed by SSL.
