---
id: webcam-streaming-resolution-framerate
title: Webcam streaming resolution and frame rate
---

:::tip
Most of the time you can leave The Spaghetti Detective plugin to pick the appropriate webcam streaming resolution and frame rate. You don't have to worry about them.
:::

:::caution
If you are using a Raspberry Pi, please keep in mind that it has a weak CPU. If the resolution and/or frame rate is set to high, it may overwhelm the Pi's CPU and hence cause print quality issues.
:::

## Find out your webcam's streaming mode.

The resolution and frame rate depends on the webcam's streaming mode.

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to find out the webcam streaming mode.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

:::info
Learn more about [advanced mode and compatibility mode](/docs/user-guides/streaming-compatibility-mode).
:::

## If the streaming mode is "**premium (advanced)**":

This means the webcam is in the Premium Streaming (advanced mode). In this mode, there are only limited options for resolutions and frame rates.

**If you want to set your own resolution and frame rate, you will need to [change the compatibility mode to "always"](/docs/user-guides/streaming-compatibility-mode#when-should-i-always-stream-in-compatibility-mode), then follow [the instructions for Premium Streaming (compatibility mode)](#if-the-streaming-mode-is-premium-compatibility-or-basic).**

:::info
The Premium Streaming (advanced mode) has to take total control of the webcam, such as the resolution, frame rate, auto-focus, etc., so that the stream can be encoded in highly-efficient H.264.
:::

:::note
If you have changed webcam settings in "octopi.txt", you may be surprised to see these settings are no longer effective in the Premium Streaming (advanced mode).
:::

### Frame rate

In the Premium Streaming (advanced mode), the frame rate is always 25 FPS (frames-per-second).

### Resolution

In the Premium Streaming (advanced mode), the webcam resolution depends on if you have a Pi Camera or a USB camera.

#### If you have a Pi Camera:

:::info
Learn more about the [Pi Camera](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera).
:::

If you have a Pi Camera, you can find or change its current resolution on the plugin's settings page.

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
2. Scroll down the navigation bar on the left side.
3. Click "Obico for OctoPrint" tab.
4. Click the "Settings" button.

![](/img/user-guides/helpdocs/tsd-plugin-open-settings-page.gif)

Pi Camera's current resolution level is in the "Premium Streaming" section.

If the webcam aspect ratio setting in OctoPrint is 4:3 (default):

* Low: 320x240
* Medium: 640x480
* High: 1296x972
* Ultra high: 1640x1232

If you have changed the webcam aspect ratio setting in OctoPrint to 16:9:

* Low: 480x270
* Medium: 960x540
* High: 1640x922
* Ultra high: 1920x1080

#### If you have a USB camera:

When you have a USB camera and its streaming mode is "Premium (advanced)", the resolution is fixed at 640x480. This is due to some technical limitations on how the Premium streaming works in advanced mode. Your best option is to leave it as is.

However, if you really want to change the resolution and/or the frame rate, follow these 2 steps:

1. [Change the compatibility mode to "always"](/docs/user-guides/streaming-compatibility-mode#when-should-i-always-stream-in-compatibility-mode).

2. Change the resolution and/or frame rate as instructed in [this section](#if-the-streaming-mode-is-premium-compatibility-or-basic).

:::info
There are simply too many USB camera models. 640x480 is the only resolution that all of them support. This is why the resolution is fixed at 640x480 in Premium Streaming (advanced mode).
:::

## If the streaming mode is "**Premium (compatibility)**" or "**Basic**":

When the webcam streaming is in "**Basic**" mode, or "**Premium (compatibility)**" mode, The Spaghetti Detective plugin won't change the resolution or the frame rate. Instead, they are set by the OctoPrint's original streaming process before The Spaghetti Detective plugin was installed.

* If you have set up OctoPrint using the official OctoPi image, head to this [OctoPrint help document](https://community.octoprint.org/t/how-can-i-change-mjpg-streamer-parameters-on-octopi/203) to learn about how you can change the resolution and/or frame rate.

* If you have replaced the original OctoPrint streaming process with a custom one, such as an IP Camera, you need to refer to the user manual of your custom streaming process to find out how you can adjust the settings.

:::danger
Raising resolution and/or frame rate above the default values may result in an excessive amount of CPU usage and potentially print quality issues.
:::

:::info
If you are running OctoPrint on a Raspberry Pi, the OctoPrint's built-in streaming program is called "mjpeg-streamer".
:::