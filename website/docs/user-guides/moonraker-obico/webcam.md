---
title: Webcam Configuration
---


:::tip
Obico webcam streaming relies on a program called "janus" to work. If janus is not installed on your system by default, you will need to manually install it:

`sudo apt install janus`
:::


## `[webcam]` in moonraker-obic.cfg

- `disable_video_streaming`: Default to `False`. Change it to `True` to disable the webcam streaming [in some rare cases](https://www.obico.io/docs/user-guides/disable-25-fps-streaming/).

:::caution
Usually, you don't need to configure the following settings in the `[webcam]` section. In that case, **Obico for Klipper** will automatically obtain them from Moonraker.
:::

Set values in this section only when **Obico for Klipper** can't obtain these configurations, which is very rare.

- `snapshot_url`

    Such as "http://127.0.0.1:8080/?action=snapshot". This URL is required for the primary webcam unless there is a matching webcam configuration in Mainsail/Fluidd. This URL needs to return a valid JPG on each request.

- `stream_url`

    Such as "http://127.0.0.1:8080/?action=stream". This URL is required for "h264_transcode" and "mjpeg_webrtc" stream mode, unless there is a matching webcam configuration in Mainsail/Fluidd.  This URL has to return a valid MJPEG stream.

- `is_nozzle_camera`

    True|False. Default: False.

    If you set it to "True", make sure this is indeed a nozzle camera. Otherwise, the first layer AI won't work properly.

- `stream_mode`

    h264_transcode|mjpeg_webrtc|h264_copy|h264_device

    By default, **Obico for Klipper**  will try "h264_transcode" first, and fallback to "mjpeg_webrtc". Please note all these stream_mode needs janus to function properly.

- `target_fps`

    Note: If you are on self-hosted Obico server, the real FPS may be limited your hardware capabilities. If you are on Obico cloud, the real FPS may be limited by the service level you have subscribed. [More info](/docs/user-guides/webcam-streaming-resolution-framerate-klipper/).

- `resolution`

    Default: Automatically detected based on the stream_url or snapshot_url.

    Note: If you are on self-hosted Obico server, the real resolution may be limited your hardware capabilities. If you are on Obico cloud, the real resolution may be limited by the service level you have subscribed. [More info](/docs/user-guides/webcam-streaming-resolution-framerate-klipper/).

- `flip_h`

    True|False. Default: False

- `flip_v`

    True|False. Default: False

- `rotation`

    0|90|180|270. Default: 0

    Clockwise rotation.

- `aspect_ratio_169`

    True|False. Default: False

- `h264_http_url`

    Required only when `stream_node=h264_copy`. It needs to be a valid Camera Streamer MP4 url, such as "http://127.0.0.1:8080/video.mp4".

- `h264_device_path`

    Required only when `stream_node=h264_device`. It needs to be a device that supports H.264 output capability.


## Configure multiple webcams

You can configure more than one webcams by additional named webcam sections. For instance:

```
[webcam name of the primary webcam]
...

[webcam name of another webcam]
...
```

The first `[webcam]` section will be your primary webcam. A primary webcam is what Obico uses for failure detection and generating timelapse videos.

**Obico for Klipper**  will try to match the name with the webcam configured in Mainsail/Fluidd. If a match is found, it will automatically retrieve settings from Mainsail/Fluidd, so that you don't have to re-configure them here.

For instance, if you have a minimum webcam section in `moonraker-obico.cfg`:

```
...

[webcam Main USB Camera]
disable_video_streaming = False

...

```


But you also have a webcam named "Main USB Camera" configured in your Mainsail/Fluidd as follows:

```
URL Stream
/webcam/?action=stream

URL Snapshot
/webcam/?action=snapshot

Rotate:
90
```

Then **Obico for Klipper**  will automatically generate an equivalent of this webcam configuration for you:

```
....

[webcam Main USB Camera]
disable_video_streaming = False
stream_url = http://127.0.0.1/webcam/?action=stream
snapshot_url = http://127.0.0.1/webcam/?action=snapshot
rotation = 90

...

```

:::caution
If the webcam section doesn't have a name, i.e., just `[webcam]`, **Obico for Klipper** will randomly select a webcam configured in Mainsail/Fluidd and use its settings. This may not be what you want if you have more than one webcams configured in Mainsail/Fluidd.

We highly recommend a matching name for your webcam configuration.
:::

:::caution
The "URL Stream" or "URL Snapshot" in Mainsail/Fluidd doesn't require the hostname part (such as `http://127.0.0.1`). But **Obico for Klipper**  does require that.

If the hostname part is not included in Mainsail/Fluidd webcam configuration, **Obico for Klipper**  will automatically use `http://127.0.0.1`. If this is not what you want, you will have to specify the `stream_url` and `snapshot_url` in `moonraker-obico.cfg` with the full URLs.
:::
