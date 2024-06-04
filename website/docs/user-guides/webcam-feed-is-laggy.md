---
id: webcam-feed-is-laggy
title: Troubleshoot choppy/jerky Premium Streaming
sidebar_label: Troubleshoot choppy/jerky Premium Streaming
---
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'

:::caution

Make sure you have gone through [this comprehensive webcam streaming troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to rule out the basic steaming problems.

For instance, if you have on the Obico Cloud's Free plan, you are only eligible for the Basic Streaming, which can appear to be quite choppy. Learn more about the difference between [Premium Streaming and Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).

:::

If the Premium Stream is choppy only very occasionally for brief moments, you can reload the page and it should resume streaming just fine. There is nothing to worry about.

However, if the problem happens frequently enough, follow this guide to identify and fix the root cause.

:::info

Just like any other live video streaming or video conferencing, the Obico Premium Streaming may be choppy or jerky occasionally when your phone or your computer doesn't have a robust Internet connection.

:::

### Possible reasons why the Premium Streaming is choppy/jerky: {#possible-reasons-why-the-premium-streaming-is-choppyjerky}

* Your phone is connected to a cellular network that has a weak reception, low bandwidth, or high latency.
* Your Raspberry Pi doesn't have a reliable Internet connection, especially if the Pi is connected via Wi-Fi.
* The webcam is not properly connected to the Raspberry Pi.
* The webcam resolution is set too high.
* The webcam streaming frame rate is set too high.

## 1. Check the webcam streaming mode {#1-check-the-webcam-streaming-mode}

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to find out your webcam's current streaming mode.

### If the webcam streaming mode is "0.1 FPS": {#if-the-webcam-streaming-mode-is-01-fps}

This means the Premium Streaming process failed to start. Follow [this troubleshooting guide](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/) to figure out why.

### If the webcam streaming mode is "Premium": {#if-the-webcam-streaming-mode-is-premium-25ps-or-premium-compatibility}

Continue to the next troubleshooting step.

## 2. Look for warning messages {#2-look-for-warning-messages}

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

This may indicate a similar connection issue as the one above. But it may also indicate a webcam configuration issue on the Raspberry Pi.

- [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
- [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).
- Make sure [the webcam resolution is not set too high](webcam-streaming-resolution-framerate-octoprint.md/#if-the-streaming-mode-is-premium-compatibility-or-basic).
- Make sure your webcam is properly connected to the Raspberry Pi, and [is properly configured in OctoPrint](/docs/user-guides/octoprint-webcam-not-streaming/#3-check-if-the-webcam-is-configured-correctly-in-octoprint).
- If you are using the mobile app, check it in the web app to see if you have the same problem. If you are using the web app, check it in the mobile app, or check it in a different browser.

## 4. Get help from a human {#4-get-help-from-a-human}

If none of the steps above helped you identify the problem, you can [get help from a human](/docs/user-guides/contact-us-for-support).
