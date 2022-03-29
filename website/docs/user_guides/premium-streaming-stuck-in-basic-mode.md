---
id: premium-streaming-stuck-in-basic-mode
title: Getting Basic Streaming when eligible for Premium Streaming
---

Follow this troubleshooting guide if your account is eligible for the Premium Streaming but you are only getting the Basic Streaming. Please make sure:

1. You are eligible for the Premium Webcam Streaming. If you are not sure, [follow this guide](/docs/webcam-feed-is-not-showing) to find out.
1. The webcam streaming is currently stuck in the "**Basic**" mode. Follow [this guide](/docs/check-webcam-streaming-mode/) to find out the current webcam streaming mode.

If any of the above is not true, you need to follow this [general webcam streaming troubleshooting guide](/docs/webcam-feed-is-not-showing/) instead. If both are confirmed, go through the following steps to figure out why and fix it.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/webcam-streaming-for-human-eyes).
:::

## 1. Restart OctoPrint

You need to restart OctoPrint after you have upgraded to the Pro plan to get the Premium Streaming to kick in.

Sometimes restarting OctoPrint is not enough. Try to reboot your Raspberry Pi in that case. If even that fails, try to unplug Raspberry Pi's power supply, wait for 30 seconds, and plug it back in.

## 2. Make sure the Premium Streaming is not disabled

By default, the Premium Streaming is enabled. Let's make sure it has not been disabled.

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click "Access Anywhere - The Spaghetti Detective" tab.
1. Click the "Settings" button.
1. Is "Disable the Premium Webcam Streaming" checked?

![](/img/user_guides/helpdocs/tsd-plugin-disable-premium-streaming.gif)

Uncheck the "Disable premium webcam streaming" if it's currently checked. Don't forget to click the "Save" button and restart OctoPrint afterward. 

:::info
When "Disable the Premium Webcam Streaming" is checked, you only get the Basic Streaming even if you are on the Pro plan.
:::

:::info
There are [a few rare reasons](/docs/disable-25-fps-streaming) why you may want to have the Premium Streaming disabled.
:::

## 3. Is OctoPrint running on a Raspberry Pi?

The Premium Webcam Streaming requires Raspberry Pi to work. It is well tested on **Raspberry Pi 4B, Raspberry Pi 3B/3B+, and Zero/Zero W**.

If you are not running OctoPrint on a Raspberry Pi, The Spaghetti Detective plugin will fall back to the Basic Streaming.

:::info
The reason why Raspberry Pi is required for the Premium Streaming is because it has a special hardware accelerator required to encode H.264 video efficiently.
:::

## 4. Try "always stream in compatibility mode"

In most cases, the Premium Streaming will automatically switch to the compatibility mode when the advanced mode fails. But there is a slight possibility it will get stuck in the "Basic" mode.

Try to [set the compatibility mode set to "**always**"](/docs/streaming-compatibility-mode#how-to-change-the-compatibility-mode-setting) to see if it'll get it out of the "Basic" streaming mode. **You need to restart the Raspberry Pi after the switch**.

:::info
Learn more about [advanced mode and compatibility mode in the Premium Streaming](/docs/streaming-compatibility-mode).
:::

## 5. Flash the SD card with an OctoPi image

The Premium Streaming may not work if you flashed your Pi with:

* a Raspbian image and custom-installed OctoPrint;
* an OctoPi version that is older than 0.15.0;
* an OctoPi release candidate (RC) version;
* or an OctoPi pre-release version.

If that's the case, grab a spare SD card, flash it with latest [official OctoPi image](https://octoprint.org/download/). Set up The Spaghetti Detective on the new OctoPrint to see if the Premium Streaming will work now.

## 6. If none of the above worked

[Get help from a human](/docs/contact-us-for-support).

