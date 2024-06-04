---
id: octoprint-webcam-not-streaming
title: Webcam streaming not working in OctoPrint
---

Follow this troubleshooting guide if the webcam streaming stops working in OctoPrint after the "Obico for OctoPrint" plugin is installed.

:::caution
This guide is for troubleshooting webcam streaming **in OctoPrint**.

If the webcam works in OctoPrint but not in the Obico mobile app or mobile app, you need to check [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing).
:::

## Check if the webcam is configured correctly in OctoPrint {#3-check-if-the-webcam-is-configured-correctly-in-octoprint}

Before checking if the webcam is configured correctly in OctoPrint, let's disable the Obico plugin to be 100% sure it is not the source of the problem.

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. On the settings page, click "**Plugin Manager**".
1. Find the "Obico for OctoPrint" plugin.
1. Disable the plugin by clicking the little toggle on the right-hand side.
1. Follow the prompt to restart OctoPrint.

![](/img/user-guides/helpdocs/disable-tsd-plugin.gif)

To test if the webcam is correctly configured in OctoPrint,

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Click the "**Webcam & Timelapse**"  tab.
1. Locate the "**Stream URL**" field.
1. Press the "**Test**" button next to it.
1. Locate the "**Snapshot URL**" field.
1. Press the "**Test**" button next to it.

![](/img/user-guides/helpdocs/test-snapshot-url.gif)

If the test failed, the webcam is not configured correctly in OctoPrint. You need to fix this problem first. The best place for find the information and/or get help is the [OctoPrint community forum](https://community.octoprint.org/).

If the test passed, please re-enable the Obico plugin and restart OctoPrint. After that, if the webcam streaming OctoPrint stops working again, it probably means you have run into a bug in the Obico plugin. In this case, [report the problem to us](mailto:support@obico.io).

:::info
If you are running OctoPrint on a Raspberry Pi, and you followed the official OctoPi setup guide, and you have one webcam (either a Pi Camera or a USB camera) directly plugged in the Pi, the default webcam configurations should work.

However, if you have a custom OctoPrint setup, such as using an IP camera, configured multiple webcams, or not using the OctoPi image, you may have inadvertently set the webcam snapshot URL to a wrong value.
:::
