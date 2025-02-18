---
title: Webcam stream is only 0.1 FPS
description: Learn how to fix the webcam stream that is stuck at 0.1 FPS.
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::info
The failure detection is not impacted in any way even if the webcam stream is stuck in 0.1 FPS. This is because the failure detection is designed to work best at 0.1 FPS.
:::

## "Janus not found" error.

The most common cause for this problem is that [Janus is not installed on your printer or SBC](/docs/user-guides/webcam-install-janus/). When this is the case, you will also see a warning in the Obico app:

![Janus Not Found](/img/user-guides/helpdocs/janus-not-found-warning.png)

The solution is to install Janus on your printer or SBC. [Follow this guide for details](/docs/user-guides/webcam-install-janus/).

## Network settings for self-hosted Obico server

Self-hosted Obico server supports Premium Streaming. However, it's possible the WebRTC connection can't be established due to your network configurations (firewall, routing, NAT configuration in your router, etc). To check if this is the case, [re-link your printer to the Obico cloud](/docs/user-guides/relink-printer/). If the issue is gone, the problem is with the settings of your server or its network configuration.

## Is the webcam streaming disabled? {#1-is-the-webcam-streaming-disabled}

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

## Are you using an OS image that doesn't support streaming? {#4-did-you-use-the-official-octopi-image-to-flash-the-sd-card}

Not all Operating Systems that can run on your printer or Raspberry Pi has the libraries required for the webcam streaming. Make sure you flashed the SD card using the supported OS images if you want to have a smooth webcam stream in Obico.

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

- 64-bit Raspberry Pi OS Debian version: 11 (bullseye)

#### OS images that *may* support the webcam streaming {#os-images-that-may-support-the-webcam-streaming}

- Raspberry Pi OS Debian version: 12 (bookworm). Both 32-bit and 64-bit.
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
- Raspberry Pi OS versions Buster.
- 32-bit Raspberry Pi OS Debian version: 11 (bullseye)

#### OS images that will NOT support the webcam streaming {#os-images-that-will-not-support-the-webcam-streaming-1}

- 64-bit Raspberry Pi OS Debian version: 11 (bullseye)

#### OS images that *may* support the webcam streaming {#os-images-that-may-support-the-webcam-streaming-1}

- Raspberry Pi OS Debian version: 12 (bookworm). Both 32-bit and 64-bit.
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
