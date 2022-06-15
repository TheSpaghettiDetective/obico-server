---
title: Webcam stream is only 0.1 FPS
---

Follow this troubleshooting guide if the webcam is streaming at a very low frame rate (about 0.1 FPS, or 1 frame per 10 seconds), and the webcam stream mode is shown as *0.1 FPS*.

:::tip
Follow [this guide](/docs/user-guides/check-webcam-streaming-mode/) to find out the current webcam streaming mode.
:::

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::


## 1. Is the webcam streaming disabled?

By default, the webcam streaming is enabled. Let's make sure it has not been disabled.

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click the "Obico for OctoPrint" tab.
1. Click the "Settings" button.
1. Is "Disable webcam streaming" checked?

![Disable video streaming](/img/user-guides/settings-disable-25-fps-streaming.png)

Uncheck the "Disable webcam streaming" if it's currently checked. Don't forget to click the "Save" button and restart OctoPrint afterward.

:::info
There are [a few rare reasons](/docs/user-guides/disable-25-fps-streaming) why you may want to have the webcam streaming disabled.
:::

## 2. Is OctoPrint running on a Raspberry Pi?

The webcam streaming requires Raspberry Pi to work. It is well tested on **Raspberry Pi 4B, Raspberry Pi 3B/3B+, and Zero/Zero W**.

If you are not running OctoPrint on a Raspberry Pi, the Obico plugin will only "stream" by taking one snapshot from the webcam every 10 seconds.

:::caution

If you have installed docker on the Raspberry Pi, and are running OctoPrint inside the docker containers, you won't get the Premium Streaming either.

:::

:::info
The reason why Raspberry Pi is required for the webcam streaming is because it has a special hardware accelerator required to encode H.264 video efficiently.
:::

## 3. Try "always stream in compatibility mode"

In most cases, the webcam streaming will automatically switch between the compatibility mode the advanced mode. But there is a slight possibility it will get stuck in the "wrong" mode and hence fail.

Try to [set the compatibility mode set to "**always**"](/docs/user-guides/streaming-compatibility-mode#how-to-change-the-compatibility-mode-setting) to see if it'll get it out of the "Basic" streaming mode. **You need to restart the Raspberry Pi after the switch**.

:::info
Learn more about [advanced mode and compatibility mode](/docs/user-guides/streaming-compatibility-mode).
:::

## 4. Did you use the official OctoPi image to flash the SD card?

The webcam streaming may not work if you flashed your Pi with:

* a Raspbian image and custom-installed OctoPrint;
* an OctoPi version that is older than 0.15.0;
* an OctoPi release candidate (RC) version;
* or an OctoPi pre-release version.

If that's the case, grab a spare SD card, flash it with latest [official OctoPi image](https://octoprint.org/download/). Set up Obico on the new OctoPrint to see if the webcam streaming will work now.

## 6. If none of the above worked

[Get help from a human](/docs/user-guides/contact-us-for-support).

