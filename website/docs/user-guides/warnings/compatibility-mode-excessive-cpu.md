---
id: compatibility-mode-excessive-cpu
title: '"Webcam streaming uses excessive CPU"'
---

<img style={{maxWidth: "420px"}} src="/img/user-guides/helpdocs/using-excessive-cpu-warning.png"></img>

The webcam streaming is a balancing act between video frame rate, webcam resolution, network bandwidth usage, and CPU usage. The rule of thumb is: the higher video frame rate and/or webcam resolution, the higher network bandwidth, and the higher CPU usage.

Most of the times the Obico plugin does a fair job at balancing between these competing factors, so that you don't have to worry about them. However, in rare occasions, the plugin can't keep CPU usage low enough after trying all options. In this case, it'll warn you about the situation so that you can take actions if needed.

There are a few things you can do to fix the problem:

* [Lower the frame rate or resolution for the "compatibility mode" in premium webcam streaming](/docs/user-guides/webcam-streaming-resolution-framerate/).
* [Change the compatibility mode settings](/docs/user-guides/streaming-compatibility-mode#how-to-change-the-compatibility-mode-setting) to "**Never use compatibility mode**".
* [Disable webcam streaming](/docs/user-guides/disable-25-fps-streaming/).

:::info
Learn more about the [Premium Streaming](/docs/user-guides/more-about-webcam-streaming/).
:::
