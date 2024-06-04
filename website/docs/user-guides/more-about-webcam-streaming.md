---
id: more-about-webcam-streaming
title: Premium Streaming FAQs
sidebar_label: Premium Streaming FAQs
---

Have questions on the Premium Streaming? Look for the answer here!

### Premium streaming is cool. But wouldn't it cost too much data usage? {#premium-streaming-is-cool-but-wouldnt-it-cost-too-much-data-usage}

Nope!

First of all, the Premium Streaming uses H.264 video encoding, which consumes less than 20% of the data usage compared to the default JPEG-based streaming in OctoPrint.

In addition, the premium video streaming is activated only when you open the browser to watch it. The streaming will automatically stop to save network data usage when you put the browser tab to the background, close the browser window, switch to a different app on your phone, or lock your phone screen. In short, if you are not watching the webcam feed, video streaming won't cost you any data usage on your phone, your home network, or your Raspberry Pi.

### What resolution and frame rate is the webcam currently streaming at? {#what-resolution-and-frame-rate-is-the-webcam-currently-streaming-at}

Follow [this guide](/docs/user-guides/webcam-streaming-resolution-framerate) to find out.

### The Premium Streaming is not working! {#the-premium-streaming-is-not-working}

Follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to figure out why. In most case, it's because the prerequisites for the Premium Streaming aren't satisfied. For instance, the OctoPrint is not running on a Raspberry Pi. In these cases, the plugin will automatically switch to the Basic Streaming.

If however, the Premium Streaming causes webcam streaming issues in OctoPrint, you can [disable it](/docs/user-guides/disable-25-fps-streaming).