---
id: webcam-feed-is-laggy
title: Troubleshoot choppy/jerky Premium Streaming
sidebar_label: Troubleshoot choppy/jerky Premium Streaming
---
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'

If the Premium Stream is choppy only very occasionally for brief moments, you can reload the page and it should resume streaming just fine. There is nothing to worry about.

However, if the problem happens frequently enough, follow this guide to identify and fix the root cause.

:::info

Just like any other live video streaming or video conferencing, the Obico Premium Streaming may be choppy or jerky occasionally when your phone or your computer doesn't have a robust Internet connection.

:::

## Webcam stream is only 0.1 FPS

If your webcam only refreshes once about every 10 seconds (0.1FPS webcam stream), follow [this guide for troubleshooting](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/).

## You don't have an Obico Pro subscription

If you are on the Obico Cloud's Free plan, you are only eligible for the Basic Streaming, which can appear to be quite choppy. Learn more about the difference between [Premium Streaming and Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).

[Upgrade to the Obico Pro plan](https://app.obico.io/ent_pub/pricing/) to get 25FPS Premium Streaming.

## The hardware or OS doesn't support H.264 encoding

By default, Obico Premium Streaming uses H.264 video encoding. This is because H.264 is highly efficient in network bandwidth. However, if the underlining hardware (printer main board or Raspberry Pi) doesn't support H.264 encoding, Obico will fall back to M-JPEG for streaming. Because M-JPEG uses 5x or more bandwidth, it can usually be streamed at up to 5 FPS, which will appears to be quite choppy.

You can set the logging level to verbose to check if this is the case. Here is how you can [do it in Obico for Klipper](/docs/user-guides/moonraker-obico/logging-file/) or [in Obico for OctoPrint](/docs/user-guides/turn-on-debug-logging/).

Look for log messages similar to:

```
WARNING  obico.webcam_stream - No ffmpeg found, or ffmpeg does NOT support h264_omx/h264_v4l2m2m encoding.
```

Currently only Raspberry Pi 3/4 and BTT Pi 2/CB2 (https://biqu.equipment/collections/control-board/products/bigtreetech-pi-2-cb2) support H.264 encoding. But more and more hardware are adding this capability.

:::info
Unlike previous Raspberry Pi models, Raspberry Pi 5 no longer supports H.264 encoding. We strongly suggest that you use Raspberry 3 or 4, because they are better fits for 3D printing than Raspberry Pi 5 is on almost every aspect.
:::

## Webcam is buffering or dropping frames {#2-look-for-warning-messages}

Quite often, the Obico mobile app or web app can identify and diagnose the streaming issues when they happen. In that case, the app will show warning messages.

Depending on the nature of a streaming issue, the app may show one of both of the follow warning messages:

<Zoom overlayBgColorEnd="var(--ifm-background-surface-color)">
<img src="/img/user-guides/helpdocs/streaming-warnings.jpg" style={{maxWidth: "308px"}} alt=""></img>
</Zoom>

### "Video frames dropped" {#video-frames-dropped}

This usually indicates a connection bandwidth bottleneck. The bottleneck can be anywhere, but often it's either your phone's cellular connection, or the Raspberry Pi's Wi-Fi connection.

- [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
- [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).

### "Buffering..." {#buffering}

The most common reason why the webcam shows "buffering" warning is because the webcam resolution and/or framerate is set too high. If you are not sure, test by [setting the resolution to 640x480, and framerate to 10FPS](/docs/user-guides/webcam-streaming-resolution-framerate/). If the webcam no longer buffers, you can find out the highest resolution/framerate your hardware can handle by increasing the resolution/framerate until the stream starts to buffer again.

Buffering can also be caused by connection issues.

- [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
- [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).
- If you are using the mobile app, check it in the web app to see if you have the same problem. If you are using the web app, check it in the mobile app, or check it in a different browser.

In some rare cases, the H.264 encoding process may run into errors. You can set the logging level to verbose ([Obico for Klipper](/docs/user-guides/moonraker-obico/logging-file/) or [Obico for OctoPrint](/docs/user-guides/turn-on-debug-logging/)) and look for log messages similar to:

```
2024-09-01 11:43:01,437     ERROR  obico.webcam_stream - STDOUT:
None
STDERR:
b'http://127.0.0.1/webcam/?action=stream: Server returned 5XX Server Error reply\n'

2024-09-01 11:43:01,438     ERROR  backoff - Giving up start_ffmpeg(...) after 5 tries (Exception: ffmpeg failed! Exit code: 1)
2024-09-01 11:43:01,438     ERROR  obico.utils -
Traceback (most recent call last):
  File "/home/pi/moonraker-obico.ssh/moonraker_obico/webcam_stream.py", line 300, in h264_transcode
    self.start_ffmpeg(rtp_port, '-re -i {stream_url} -filter:v fps={fps} -b:v {bitrate} -pix_fmt yuv420p -s {img_w}x{img_h} {encoder}'.format(stream_url=stream_url, fps=fps, bitrate=bitrate, img_w=img_w, img_h=im
g_h, encoder=webcam.streaming_params.get('h264_encoder')))
  File "/home/pi/.local/lib/python3.9/site-packages/backoff/_sync.py", line 94, in retry
    ret = target(*args, **kwargs)
  File "/home/pi/moonraker-obico.ssh/moonraker_obico/webcam_stream.py", line 323, in start_ffmpeg
    raise Exception('ffmpeg failed! Exit code: {}'.format(returncode))
Exception: ffmpeg failed! Exit code: 1
```

If this is the case, your best bet is to [get help from a human](/docs/user-guides/contact-us-for-support).


## Get help from a human {#4-get-help-from-a-human}

If none of the steps above helped you identify the problem, you can [get help from a human](/docs/user-guides/contact-us-for-support).
