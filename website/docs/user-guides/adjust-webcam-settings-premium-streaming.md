---
id: adjust-webcam-settings-premium-streaming
title: Adjust advanced webcam settings
---

If you just want to adjust the resolution and frame rate, you should check out [this guide](/docs/user-guides/webcam-streaming-resolution-framerate).

If you want to learn about adjusting advanced webcam settings, such as auto focus, read on.

:::danger
Adjusting advanced webcam settings may result in an excessive amount of CPU usage and potentially print quality issues.
:::

## Make sure the webcam is not in the **Premium Streaming (advanced mode)**"

1. Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to check the webcam streaming mode.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

:::info
Learn more about [advanced mode and compatibility mode](/docs/user-guides/streaming-compatibility-mode).
:::

2. If the streaming mode is "**premium (advanced)**", [change the compatibility mode to "always"](/docs/user-guides/streaming-compatibility-mode#when-should-i-always-stream-in-compatibility-mode). Otherwise, skip to [changing the webcam settings](/docs/user-guides/adjust-webcam-settings-premium-streaming#change-the-webcam-settings).

3. Restart the Raspberry Pi (only if you have changed the compatibility mode in the previous step).

4. [Check the streaming mode](/docs/user-guides/check-webcam-streaming-mode) again to make sure it's now in "**Premium (compatibility)**" or "**Basic**" mode.

## Change the webcam settings

When the webcam streaming is in "**Basic**" mode, or "**Premium (compatibility)**" mode, The Spaghetti Detective plugin won't change the resolution or the frame rate. Instead, they are set by the OctoPrint's original streaming process before The Spaghetti Detective plugin was installed.

* If you have set up OctoPrint using the official OctoPi image, head to this [OctoPrint help document](https://community.octoprint.org/t/how-can-i-change-mjpg-streamer-parameters-on-octopi/203) to learn about adjusting the advanced settings.

* If you have replaced the original OctoPrint streaming process with a custom one, such as an IP Camera, you need to refer to the user manual of your custom streaming process to find out how you can adjust the settings.

:::info
If you are running OctoPrint on a Raspberry Pi, and you haven't changed the original streaming process, the OctoPrint's built-in streaming program is called "mjpeg-streamer".
:::