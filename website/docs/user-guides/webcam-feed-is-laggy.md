---
id: webcam-feed-is-laggy
title: Troubleshoot choppy/jerky Premium Streaming
sidebar_label: Troubleshoot choppy/jerky Premium Streaming
---
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'

If the Premium Stream is choppy only very occasionally for brief moments, you can reload the page and it should resume streaming just fine. There is nothing to worry about.

However, if the problem happens frequently enough, follow this guide to identify and fix the root cause.

:::caution

Make sure you have gone through [this comprehensive webcam streaming troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to rule out the basic steaming problems.

:::

:::info

Just like any other live video streaming or video conferencing, The Spaghetti Detective Premium Streaming may be choppy or jerky occasionally when your phone or your computer doesn't have a robust Internet connection.

:::

### Possible reasons why the Premium Webcam Streaming is choppy/jerky:

* Your phone is connected to a cellular network that has a weak reception, low bandwidth, or high latency.
* Your Raspberry Pi doesn't have a reliable Internet connection, especially if the Pi is connected via Wi-Fi.
* The webcam is not properly connected to the Raspberry Pi.
* The webcam resolution is set too high.
* The webcam streaming frame rate is set too high. This can happen only when the webcam is [streamed in compatibility mode](/docs/user-guides/streaming-compatibility-mode).


## 1. Check the webcam streaming mode

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to find out your webcam's current streaming mode.

### If the webcam streaming mode is "Basic Streaming":

Basic Streaming is fixed at 0.1 fps (1 frame every 10 seconds). That's why it appears to be very choppy.

You need to [upgrade to the Pro plan to get the buttery-smooth, 25 fps Premium Streaming](https://app.obico.io/ent_pub/pricing/).

:::info

Learn more about the difference between [Premium Streaming and Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).

:::

If you are already on the Pro plan, follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to figure out why the webcam is still in the Basic Streaming mode.

### If the webcam streaming mode is "Premium (25ps)" or "Premium (compatibility)":

Continue to the next troubleshooting step.

## 2. Are you using a Raspberry Pi?

Raspberry Pi is required for the Premium Streaming. If you are not running OctoPrint on a Raspberry Pi, you will only get the Basic Streaming, which will be choppy as it only streams at 0.1 fps.

Continue to the next step if you are using a Raspberry Pi.

:::caution

If you have installed docker on the Raspberry Pi, and are running OctoPrint inside the docker containers, you won't get the Premium Streaming either.

:::

:::info
The reason why Raspberry Pi is required for the Premium Streaming is because it has a special hardware accelerator required to encode H.264 video efficiently.
:::

## 3. Look for warning messages

Quite often, The Spaghetti Detective mobile app or web app can identify and diagnose the streaming issues when they happen. In that case, the app will show warning messages.

Depending on the nature of a streaming issue, the app may show one of both of the follow warning messages:

<Zoom overlayBgColorEnd="var(--ifm-background-surface-color)">
<img src="/img/user-guides/helpdocs/streaming-warnings.jpg" style={{maxWidth: "308px"}} alt=""></img>
</Zoom>

### "Video frames dropped"

This usually indicates a connection bandwidth bottleneck. The bottleneck can be anywhere, but often it's either your phone's cellular connection, or the Raspberry Pi's Wi-Fi connection.

- [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
- [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).

### "Buffering..."

This may indicate a similar connection issue as the one above. But it may also indicate a webcam configuration issue on the Raspberry Pi.

- [Test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed).
- [Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed).
- Make sure your webcam is properly connected to the Raspberry Pi, and [is properly configured in OctoPrint](/docs/user-guides/octoprint-webcam-not-streaming/#3-check-if-the-webcam-is-configured-correctly-in-octoprint).
- If everything is ruled out, try to [set the streaming to "**Always stream in compatibility mode**"](/docs/user-guides/streaming-compatibility-mode/#how-to-change-the-compatibility-mode-setting). Restart OctoPrint and see if the "Buffering" warning goes away and the Premium Stream is smooth now.

## 4. Get help from a human

If none of the steps above helped you identify the problem, you can [get help from a human](/docs/user-guides/contact-us-for-support).
