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

### Now I have the awesome 25 fps streaming. But the webcam feed in OctoPrint becomes slower. Why? {#now-i-have-the-awesome-25-fps-streaming-but-the-webcam-feed-in-octoprint-becomes-slower-why}

The Premium Streaming is based on H.264, which is much more efficient than the original OctoPrint webcam feed (based on JPEG). However, these 2 streaming mechanisms are not compatible with each other so they can't co-exist.

When you try to watch the webcam stream in OctoPrint, the H.264 video stream has to be converted into JPEG format, since OctoPrint can only stream JPEG. This process takes a significant amount of CPU power, so we can't do it at a frame rate as high as the original OctoPrint webcam feed without using too much Raspberry Pi CPU and negatively affect the print quality.

If this is a big problem for you, you can consider [changing the settings "**Always stream in compatibility mode**"](/docs/user-guides/streaming-compatibility-mode/#when-should-i-always-stream-in-the-compatibility-mode).

:::caution
"Always streaming in compatibility mode" should be set with caution. It puts significantly more CPU load on the Raspberry Pi and may cause print quality issues if the resolution and/or frame rate is set too high.
:::


### What is compatibility mode and why I should care? {#what-is-compatibility-mode-and-why-i-should-care}

Learn more about [the advanced mode and the compatibility mode](/docs/user-guides/streaming-compatibility-mode).

### I configured webcam settings in "octopi.txt", such as resolution or aspect ratio. But they are lost in the Premium Streaming! {#i-configured-webcam-settings-in-octopitxt-such-as-resolution-or-aspect-ratio-but-they-are-lost-in-the-premium-streaming}

This is because the streaming settings in "octopi.txt" are ignored when the Premium Streaming is in the advanced mode.

Learn [how to adjust the webcam settings in Premium Streaming](/docs/user-guides/webcam-streaming-resolution-framerate).

:::tip
If you want to adjust webcam settings using "octopi.txt", you can should [set compatibility mode to "always"](/docs/user-guides/streaming-compatibility-mode/#when-should-i-always-stream-in-the-compatibility-mode).
:::

### What resolution and frame rate is the webcam currently streaming at? {#what-resolution-and-frame-rate-is-the-webcam-currently-streaming-at}

Follow [this guide](/docs/user-guides/webcam-streaming-resolution-framerate) to find out.

### The Premium Streaming is not working! {#the-premium-streaming-is-not-working}

Follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing) to figure out why. In most case, it's because the prerequisites for the Premium Streaming aren't satisfied. For instance, the OctoPrint is not running on a Raspberry Pi. In these cases, the plugin will automatically switch to the Basic Streaming.

If however, the Premium Streaming causes webcam streaming issues in OctoPrint, you can [disable it](/docs/user-guides/disable-25-fps-streaming).