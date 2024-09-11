---
id: webcam-streaming-for-human-eyes
title: Premium Streaming vs Basic Streaming
sidebar_label: Premium Streaming vs Basic Streaming
---

There are a few critical differences between the **Premium Streaming** and the **Basic Streaming**:

| | Premium Streaming | Basic Streaming |
|-|-------|---------|
| Eligibility | Pro subscribers only | Free users |
| Frame rate | Up to 25 FPS (frames per second) | Up to 5 FPS (frames per second) |
| Throttle | Always available. No any throttle or limitation. | Throttled for 30 seconds every minute * |

* The Basic Streaming plays the video for up to 30 seconds at a time. You will need to wait for another 30 seconds before you can resume the video.

:::info
The Premium Streaming in Obico is based on H.264 video encoding, which is highly efficient in network bandwidth.

Whereas the Basic Streaming in OctoPrint or Klipper (Mainsail or Fluidd) is based on M-JPEG encoding, which uses 5x more network bandwidth and mobile data.
:::

:::info
The Premium Streaming uses a great amount of resources on the Obico Server, such as the cloud storage and the network bandwidth. This is why we can make it available only to the Pro subscribers.
:::

## Premium Streaming FAQs {#premium-streaming-faqs}

### Premium streaming is cool. But wouldn't it cost too much data usage? {#premium-streaming-is-cool-but-wouldnt-it-cost-too-much-data-usage}

Nope!

First of all, the Premium Streaming uses H.264 video encoding, which consumes less than 20% of the data usage compared to the default JPEG-based streaming in OctoPrint.

In addition, the premium video streaming is activated only when you open the browser to watch it. The streaming will automatically stop to save network data usage when you put the browser tab to the background, close the browser window, switch to a different app on your phone, or lock your phone screen. In short, if you are not watching the webcam feed, video streaming won't cost you any data usage on your phone, your home network, or your Raspberry Pi.

### What resolution and frame rate is the webcam currently streaming at? {#what-resolution-and-frame-rate-is-the-webcam-currently-streaming-at}

Follow [this guide](/docs/user-guides/webcam-streaming-resolution-framerate) to find out.

### Is Premium streaming available for the self-hosted Obico server? {#is-premium-streaming-available-for-the-self-hosted-obico-server}

Yes. If it doesn't work on your self-hosted Obico server, follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to figure out why.

### The Premium Streaming is not working! {#the-premium-streaming-is-not-working}

Follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to figure out why. In most case, it's because the prerequisites for the Premium Streaming aren't satisfied. For instance, the OctoPrint is not running on a Raspberry Pi. In these cases, the plugin will automatically switch to the Basic Streaming.

If however, the Premium Streaming causes webcam streaming issues in OctoPrint, you can [disable it](/docs/user-guides/disable-25-fps-streaming).