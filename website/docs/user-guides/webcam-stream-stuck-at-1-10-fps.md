---
title: Webcam stream is only 0.1 FPS
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Follow this troubleshooting guide if the webcam is streaming at a very low frame rate (about 0.1 FPS, or 1 frame per 10 seconds), and the webcam stream mode is shown as *0.1 FPS*.

:::info
The failure detection is not impacted in any way even if the webcam stream is stuck in 0.1 FPS. This is because the failure detection is designed to work best at 0.1 FPS.
:::

:::tip
Follow [this guide](/docs/user-guides/check-webcam-streaming-mode/) to find out the current webcam streaming mode.
:::

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::


## 1. Is the webcam streaming disabled? {#1-is-the-webcam-streaming-disabled}

By default, the webcam streaming is enabled. Let's make sure it has not been disabled.

<Tabs
  defaultValue="octoprint"
  groupId="agent"
  values={[
    {label: 'Obico for OctoPrint', value: 'octoprint'},
    {label: 'Obico for Klipper', value: 'klipper'},
  ]}>
  <TabItem value="octoprint">

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click the "Obico for OctoPrint" tab.
1. Click the "Settings" button.
1. Is "Disable webcam streaming" checked?

![Disable video streaming](/img/user-guides/settings-disable-25-fps-streaming.png)

Uncheck the "Disable webcam streaming" if it's currently checked. Don't forget to click the "Save" button and restart OctoPrint afterward.

  </TabItem>
  <TabItem value="klipper">

1. Open the `moonraker-obico.cfg` file.
2. If the "[webcam] -> disable_video_streaming" setting is set to `True`, either remove this setting, or set it to `False` (default value).
3. Restart the Raspberry Pi.

:::info

Learn more about [the config file for Obico for Klipper](moonraker-obico/config.md).

:::

  </TabItem>
</Tabs>

:::info
There are [a few rare reasons](/docs/user-guides/disable-25-fps-streaming) why you may want to have the webcam streaming disabled.
:::

## 2. Are you using an OS image that doesn't support streaming? {#4-did-you-use-the-official-octopi-image-to-flash-the-sd-card}

Not all Operating Systems that can run on a Raspberry Pi has the libraries required for the webcam streaming. Make sure you flashed the SD card using the supported OS images if you want to have a smooth webcam stream in Obico.

<Tabs
  defaultValue="octoprint"
  groupId="agent"
  values={[
    {label: 'Obico for OctoPrint', value: 'octoprint'},
    {label: 'Obico for Klipper', value: 'klipper'},
  ]}>
  <TabItem value="octoprint">

#### OS images that have been verified to support the webcam streaming {#os-images-that-have-been-verified-to-support-the-webcam-streaming}

- All OctoPi release versions 0.15.0 or newer.

#### OS images that will NOT support the webcam streaming {#os-images-that-will-not-support-the-webcam-streaming}

- 64-bit Raspberry Pi OS. All versions.
- 32-bit Raspberry Pi OS Bullseye.

#### OS images that *may* support the webcam streaming {#os-images-that-may-support-the-webcam-streaming}

- All OctoPi beta/RC versions.
- All OctoPi release versions older than 0.15.0.
- All 32-bit Raspberry Pi OS version Buster or earlier.
- All Raspbian versions.
- All other Debian derivatives, such as DietPi.

<p />

  </TabItem>
  <TabItem value="klipper">

#### OS images that have been verified to support the webcam streaming {#os-images-that-have-been-verified-to-support-the-webcam-streaming-1}

- MainsailOS x86 version 0.6.0 or newer.
- FluiddPi version 1.17.0 or newer.
- All Raspberry Pi OS versions Buster or newer.

#### OS images that will NOT support the webcam streaming {#os-images-that-will-not-support-the-webcam-streaming-1}

None.

#### OS images that *may* support the webcam streaming {#os-images-that-may-support-the-webcam-streaming-1}

- All MainsailOS x86 versions older than 0.6.0.
- All FluiddPi versions older than 1.17.0.
- 32-bit Raspberry Pi OS versions older than Buster.
- All Raspbian versions.
- All other Debian derivatives, such as DietPi.

<p />
  </TabItem>
</Tabs>


If you are not sure if the OS causes the webcam stream to be stuck at 0.1 FPS, grab a spare SD card, flash it with one of the supported OS images, and see if you are getting a smooth webcam stream in the Obico app now.

## 3. If none of the above worked {#6-if-none-of-the-above-worked}

[Get help from a human](/docs/user-guides/contact-us-for-support).
