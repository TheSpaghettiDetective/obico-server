---
title: Webcam Configuration
---


:::tip
Obico webcam streaming relies on a program called "janus" to work. If janus is not installed on your system by default, you will need to manually install it:

`sudo apt install janus`
:::


## `[webcam]` Section in moonraker-obico.cfg {#webcam-section-in-moonraker-obicocfg}

### `disable_video_streaming` {#disable_video_streaming}

**Possible values**:

- `True`: Disable the webcam streaming [in some rare cases](https://www.obico.io/docs/user-guides/disable-25-fps-streaming/).
- `False`:

**Default value**:

- `False`

:::caution
Usually, you don't need to configure the following settings in the `[webcam]` section. In that case, **Obico for Klipper** will automatically obtain them from Moonraker.
:::

Set values in this section only when **Obico for Klipper** can't obtain these configurations, which is very rare.

### `snapshot_url` {#snapshot_url}

Such as "http://127.0.0.1:8080/?action=snapshot". This URL is required for the primary webcam unless there is a matching webcam configuration in Mainsail/Fluidd. This URL needs to return a valid JPG on each request.

### `stream_url` {#stream_url}

Such as "http://127.0.0.1:8080/?action=stream". This URL is required for "h264_transcode" and "mjpeg_webrtc" stream mode, unless there is a matching webcam configuration in Mainsail/Fluidd.  This URL has to return a valid MJPEG stream.

### `is_nozzle_camera` {#is_nozzle_camera}

If you set it to "True", make sure this is indeed a nozzle camera. Otherwise, the first layer AI won't work properly.

**Possible values**:

- `True`
- `False`

**Default value**:

- `False`

### `stream_mode` {#stream_mode}

**Possible values**:

- `h264_transcode`
- `mjpeg_webrtc`
- `h264_copy`
- `h264_device`

**Default value**:

**Obico for Klipper**  will try "h264_transcode" first, and fallback to "mjpeg_webrtc". Please note all these stream_mode needs janus to function properly.

### `target_fps` {#target_fps}

Note: If you are on self-hosted Obico server, the real FPS may be limited your hardware capabilities. If you are on Obico cloud, the real FPS may be limited by the service level you have subscribed. [More info](/docs/user-guides/webcam-streaming-resolution-framerate-klipper/).

### `resolution` {#resolution}

**Default value**:

Automatically detected based on the stream_url or snapshot_url.

Note: If you are on self-hosted Obico server, the real resolution may be limited your hardware capabilities. If you are on Obico cloud, the real resolution may be limited by the service level you have subscribed. [More info](/docs/user-guides/webcam-streaming-resolution-framerate-klipper/).

### `flip_h` {#flip_h}

**Possible values**:

- `True`
- `False`

**Default value**:

- `False`

### `flip_v` {#flip_v}

**Possible values**:

- `True`
- `False`

**Default value**:

- `False`


### `rotation` {#rotation}

Clockwise rotation.

**Possible values**:

- `0`
- `90`
- `180`
- `270`

**Default value**:

- `0`


### `aspect_ratio_169` {#aspect_ratio_169}


**Possible values**:

- `True`
- `False`

**Default value**:

- `False`

### `h264_http_url` {#h264_http_url}

Required only when `stream_node=h264_copy`. It needs to be a valid Camera Streamer MP4 url, such as "http://127.0.0.1:8080/video.mp4".

### `h264_device_path` {#h264_device_path}

Required only when `stream_node=h264_device`. It needs to be a device that supports H.264 output capability.


## Configure multiple webcams {#configure-multiple-webcams}

:::tip
Before configuring multiple webcams in Obico, they need to be configured in Mainsail/fluidd. Watch this [video for a guide on configuring multiple webcams in Mainsail/fluidd](https://youtu.be/06D01zrQTqg?si=JpvhdhpLXazZbvmA
).
:::

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


And you also have a webcam named "Main USB Camera" configured in your Mainsail/Fluidd as follows:

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

:::tip
The name matching is case-sensitive.
:::

:::caution
If the webcam section doesn't have a name, i.e., just `[webcam]`, **Obico for Klipper** will randomly select a webcam configured in Mainsail/Fluidd and use its settings. This may not be what you want if you have more than one webcams configured in Mainsail/Fluidd.

We highly recommend a matching name for your webcam configuration.
:::

:::caution
The "URL Stream" or "URL Snapshot" in Mainsail/Fluidd doesn't require the hostname part (such as `http://127.0.0.1`). But **Obico for Klipper**  does require that.

If the hostname part is not included in Mainsail/Fluidd webcam configuration, **Obico for Klipper**  will automatically use `http://127.0.0.1`. If this is not what you want, you will have to specify the `stream_url` and `snapshot_url` in `moonraker-obico.cfg` with the full URLs.
:::


## Single and Multi-Camera Configuration Examples {#single-and-multi-camera-configuration-examples}

Below are examples of valid moonraker-obico.cfg configurations

### Two Cameras: Webcam and Nozzle Camera {#two-cameras-webcam-and-nozzle-camera}

![](/img/user-guides/mainsail_nozzle_camera_usb_camera_using_port.png)

In this example, I have two webcams configured in Mainsail, one logitech c270 usb webcam and one Mintion Nozzle camera for first layer AI.

**Mainsail Webcam Configuration**:

**Webcam**: c270
**URL Stream**:  /webcam/?action=stream
**URL Snapshot**:  /webcam/?action=snapshot

**Webcam**: nozzle
**URL Stream**:  /webcam2/?action=stream
**URL Snapshot**:  /webcam2/?action=snapshot

#### moonraker-obico.cfg Webcam Section {#moonraker-obicocfg-webcam-section}

```
[webcam c270]
disable_video_streaming = False

[webcam nozzle]
disable_video_streaming = False
```

If the webcams are not picked up in the Obico app after restarting moonraker-obico, you may need to add the snapshot_url and stream_url to each webcam configuration

I access the mainsail interface at: 192.168.1.123
So, I have configured moonraker-obico.cfg as:

```
[webcam c270]
disable_video_streaming = False
stream_url = http://192.168.123/webcam/?action=stream
snapshot_url = http://192.168.123/webcam/?action=snapshot

[webcam nozzle]
disable_video_streaming = False
stream_url = http://192.168.123/webcam2/?action=stream
snapshot_url = http://192.168.123/webcam2/?action=snapshot
is_nozzle_camera = True

```

### Multiple Webcams in Mainsail/fluidd - One webcam in Obico {#multiple-webcams-in-mainsailfluidd---one-webcam-in-obico}

If you have two webcams configured in Mainsail or fluidd, but you only want one specific webcam to be shown in Obico at all times, simply add the name of the webcam from Mainsail/fluidd to the ```moonraker-obico.cfg``` file.


**Mainsail Webcam Configuration**:

```
Webcam: c270
URL Stream: /webcam/?action=stream
URL Snapshot:  /webcam/?action=snapshot
```

```
Webcam: nozzle
URL Stream:  /webcam2/?action=stream
URL Snapshot:  /webcam2/?action=snapshot
```

#### moonraker-obico.cfg Webcam Section {#moonraker-obicocfg-webcam-section-1}

If I want to only see the c270 webcam in Obico, the configuration is as follows:

```
[webcam c270]
disable_video_streaming = False
```

If the webcam is not picked up in the Obico app after restarting moonraker-obico, you may need to add the snapshot_url and stream_url to the webcam configuration.

I access the mainsail interface at: 192.168.1.123
So, I have configured moonraker-obico.cfg as:

```
[webcam c270]
disable_video_streaming = False
stream_url = http://192.168.123/webcam/?action=stream
snapshot_url = http://192.168.123/webcam/?action=snapshot
```



### Creality K1 with fluidd - Stock Camera {#creality-k1-with-fluidd---stock-camera}

In this example, I have a Creality K1 Max with the stock webcam installed.


**Fluidd Webcam Configuration**:

```
Webcam: K1 Webcam
URL Stream: /webcam/?action=stream
URL Snapshot:  /webcam/?action=snapshot
```

#### moonraker-obico.cfg Webcam Section {#moonraker-obicocfg-webcam-section-2}

```
[webcam K1 Webcam]
disable_video_streaming = False
```

If the webcam is not picked up in the Obico app after restarting moonraker-obico, you may need to add the snapshot_url and stream_url to the webcam configuration.

Fluidd is accesssed at: http://192.168.1.123:4408 so I have configured the webcam section of ```moonraker-obico.cfg``` as follows:

```
[webcam K1 Webcam]
disable_video_streaming = False
snapshot_url = http://192.168.1.123:4408/webcam/?action=snapshot
stream_url = http://192.168.1.123:4408/webcam/?action=stream
```

### Creality K1 with fluidd - Stock Camera Plus Nozzle Camera {#creality-k1-with-fluidd---stock-camera-plus-nozzle-camera}

![](/img/user-guides/fluidd_k1_max_two_webcams.png)

In this example, I have a Creality K1 Max with the stock webcam and an additional nozzle camera installed.


**Fluidd Webcam Configuration**:

```
Webcam: K1 Webcam
URL Stream: /webcam/?action=stream
URL Snapshot:  /webcam/?action=snapshot
```

```
Webcam: nozzle
URL Stream: /webcam2/?action=stream
URL Snapshot:  /webcam2/?action=snapshot
```

#### moonraker-obico.cfg Webcam Section {#moonraker-obicocfg-webcam-section-3}

```
[webcam K1 Webcam]
disable_video_streaming = False

[webcam nozzle]
disable_video_streaming = False
```

If the webcam is not picked up in the Obico app after restarting moonraker-obico, you may need to add the snapshot_url and stream_url to the webcam configuration.

Fluidd is accesssed at: http://192.168.1.123:4408 so I have configured the webcam section of ```moonraker-obico.cfg``` as follows:

```
[webcam K1 Webcam]
disable_video_streaming = False
snapshot_url = http://192.168.1.123:4408/webcam/?action=snapshot
stream_url = http://192.168.1.123:4408/webcam/?action=stream

[webcam nozzle]
disable_video_streaming = False
snapshot_url = http://192.168.1.123:4408/webcam2/?action=snapshot
stream_url = http://192.168.1.123:4408/webcam2/?action=stream
```
