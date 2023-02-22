---
id: internet-speed-requirement-premium-streaming
title: Internet speed requirements for webcam streaming
---

In order to get a buttery-smooth webcam stream, you need to make sure the Internet connection speed is fast enough. Otherwise, the webcam stream may become choppy, or even get completely stuck.

The minimum Internet speed required for a solid Premium Stream depends on 3 factors:

* [The streaming mode](/docs/user-guides/check-webcam-streaming-mode)
* [The webcam resolution](/docs/user-guides/webcam-streaming-resolution-framerate)
* [The streaming frame rate](/docs/user-guides/webcam-streaming-resolution-framerate)

:::info

There are actually 2 kinds of connection speed:

* The Internet download speed on your phone or your computer, whichever you are using The Spaghetti Detective app on.
* The Internet upload speed on your Raspberry Pi. This is often overlooked. And trickier to find out too.

:::

## If the streaming mode is "premium (advanced)", {#if-the-streaming-mode-is-premium-advanced}

For every 100k pixels webcam resolution, you need 2Mbps Internet speed to have a solid Premium Stream.

For instance,

| Resolution | # of Pixels | frame rate | speed requirement |
|------------|-------------|--------|-----------|
| 320x240 (low) | ~77k | 25 FPS | 1.6Mbps |
| 640x480 (medium) | ~300k | 25 FPS | 6Mbps |
| 1296x972 (high) | ~1,260k | 25 FPS | 26Mbps |
| 1640x1232 (ultra high) | ~2,000k | 25 FPS | 40Mbps |

:::info

The Premium Streaming is in advanced mode. In this mode, the frame rate is always 25 fps (frames-per-seconds).
:::

## If the streaming is in "Premium (compatibility)": {#if-the-streaming-is-in-premium-compatibility}

For every 100k pixels webcam resolution and 10 fps, you need 0.75Mbps Internet speed.

For instance,

| Resolution | # of Pixels | frame rate | speed requirement |
|------------|-------------|--------|-----------|
| 320x240 (low) | ~77k | 10fps | 0.6Mbps |
| 320x240 (low) | ~77k | 20fps | 1.2Mbps |
| 640x480 (medium) | ~300k | 10fps | 2.3Mbps |
| 640x480 (medium) | ~300k | 20fps | 4.6Mbps |
| 1296x972 (high) | ~1,260k | 10fps | 9.5Mbps |
| 1296x972 (high) | ~1,260k | 20fps | 19Mbps |
| 1640x1232 (ultra high) | ~2,000k | 10fps | 15Mbps |
| 1640x1232 (ultra high) | ~2,000k | 20fps | 30Mbps |

:::info
When the webcam streaming is in "Premium (compatibility)" mode, The Spaghetti Detective plugin doesn't control the webcam's resolution or frame rate. Instead, they are set by the OctoPrint's original streaming process.
:::

## If the streaming is in "Basic": {#if-the-streaming-is-in-basic}

Basic Streaming doesn't have any requirement on the Internet connection speed. Almost anywhere you have an Internet connection, the Basic Streaming will work.

:::info

See also:

* [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
* [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).

:::
