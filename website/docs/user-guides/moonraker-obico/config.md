---
id: config
title: Configurations
---

Following Klipper toolchain's convention, the configuration file for **Obico for Klipper** is typically located at `~/klipper_config/moonraker-obico.cfg`

:::caution
You need to restart the service for any change to take effect:

`systemctl restart moonraker-obico`
:::

An example of the configuration file:

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
#   In most cases webcam configuration will be automatically retrived from moonraker
#
# snapshot_url = http://127.0.0.1:8080/?action=snapshot
# stream_url = http://127.0.0.1:8080/?action=stream
# flip_h = False
# flip_v = False
# rotate_90 = False
# aspect_ratio_169 = False

[logging]
path = /home/pi/klipper_logs/moonraker-obico.log
level = INFO
```

## `[server]` section {#server-section}

The configuration for connecting to the Obico Server.

- `url`: The URL for the Obico Server. Such as "https://app.obico.io".
- `auth_token`: The authentication token to authenticate Obico for Klipper client to the Obico Server. This is typically obtained by the `install.sh` from the server during the linking process. Don't directly set it.

## `[moonraker]` section {#moonraker-section}

- `host`: Moonraker host. Usually it's "127.0.0.1", namely the same host as **Obico for Klipper**.
- `port`: The port Moonraker is listening on. The default port for Moonraker is 7125 but can be a different one, which is very typical on a system that runs multiple Moonraker instances.

## `[webcam]` section {#webcam-section}

- `disable_video_streaming`: Default to `False`. Change it to `True` to disable the webcam streaming [in some rare cases](https://www.obico.io/docs/user-guides/disable-25-fps-streaming/).

:::caution
Usually, you don't need to configure the following settings in the `[webcam]` section. In that case, **Obico for Klipper** will automatically obtain them from Moonraker.
:::

Set values in this section only when **Obico for Klipper** can't obtain these configurations, which is very rare.

- `snapshot_url`:
- `stream_url`:
- `flip_h`:
- `flip_v`:
- `rotate_90`:
- `aspect_ratio_169`:

## `[logging]` section {#logging-section}

- `path`: The path to the log file. Will be automatically rotated at 5MB size.
- `level`: Default to `INFO`. Set to `DEBUG` to see *a lot* more details in the logs
