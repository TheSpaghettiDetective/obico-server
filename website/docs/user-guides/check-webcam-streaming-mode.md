---
id: check-webcam-streaming-mode
title: Check the webcam streaming mode
---

## 1. Open the troubleshooting page. {#1-open-the-troubleshooting-page}

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click "Obico for OctoPrint" tab.
1. Click the "Troubleshooting" button.

![](/img/user-guides/helpdocs/open-troubleshooting-page.gif)

## 2. Check "Webcam streaming" in the "Plugin Status" column {#2-check-webcam-streaming-in-the-plugin-status-column}

<img style={{maxWidth: "332px", padding: "16px",}} src="/img/user-guides/helpdocs/tsd-plugin-webcam-streaming-mode-advanced.png"></img>
<img style={{maxWidth: "332px", padding: "16px",}} src="/img/user-guides/helpdocs/tsd-plugin-webcam-streaming-mode-basic.png"></img>
<img style={{maxWidth: "332px", padding: "16px",}} src="/img/user-guides/helpdocs/tsd-plugin-webcam-streaming-mode-01fps.png"></img>

The status can be one of the following:

* "**premium**" - Premium Streaming.
* "**Basic**" - Basic Streaming.
* "**0.1FPS**" - [Video streaming failed to start](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/). The Obico plugin is now "streaming" by taking snapshots at 0.1FPS.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::