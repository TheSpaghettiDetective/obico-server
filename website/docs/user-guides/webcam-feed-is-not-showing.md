---
id: webcam-feed-is-not-showing
title: Troubleshoot webcam streaming issues
---

In most cases, Obico will automatically figure out how to stream the webcam to the Obico app, such as the resolution, framerate, the bandwidth requirements, etc. However, if you run into webcam streaming issues, use this guide to find the right fix.

## What are you seeing?

Pick the symptom that best matches your problem:

- **["Webcam Streaming Failed" notification in the Obico app](#webcam-streaming-failed)**
- **[No webcam / black screen in the Obico app](#no-webcam)**
- **[Webcam only refreshes about every 10 seconds (0.1 FPS)](#0.1-fps)**
- **[Webcam stream is choppy or buffering](#choppy-premium)**

## "Webcam Streaming Failed" notification {#webcam-streaming-failed}

If you see a **Webcam Streaming Failed** notification in the Obico app, work through these steps:

### Step 1: Confirm the webcam works locally

Check that the webcam stream works in Mainsail, Fluidd, or OctoPrint — not just in the Obico app. If it doesn't work there either, fix your webcam setup first (USB connection, camera service, etc.).

On the Pi or SBC, open the webcam stream URL in a browser (the same URL Mainsail/Fluidd uses, usually `http://127.0.0.1/webcam/?action=stream`). You should see a live video feed. If it fails here, the problem is with your webcam service — not Obico.

### Step 2: Restart in the right order

On Klipper setups:

1. Restart the webcam service (`sudo systemctl restart crowsnest` or `camera-streamer`)
2. Restart moonraker-obico (`sudo systemctl restart moonraker-obico`)

On OctoPrint: restart OctoPrint.

If the notification only appears right after boot, the webcam service may not be ready when Obico starts. The restart order above usually fixes it. Also make sure the webcam service is enabled on boot (`sudo systemctl enable crowsnest` or `camera-streamer`).

### Step 3: Check your stream URL (if you use a custom or remote camera)

If you configured a custom or remote webcam URL in Obico (not the default local one), open that URL in a browser **from the Pi or SBC** — not from your laptop. If it doesn't load there, Obico can't reach it either.

See the [Obico for Klipper webcam configuration guide](/docs/user-guides/moonraker-obico/webcam/) for valid `stream_url` values (e.g. `http://127.0.0.1/webcam/?action=stream`).

### Step 4: Pick what you still see in the Obico app

The notification can mean several different things. Jump to the section that matches what you see **after** the steps above:

- Webcam missing or black screen → [No webcam in the Obico app](#no-webcam)
- Stream updates only about every 10 seconds → [0.1 FPS troubleshooting](#0.1-fps)
- Stream plays but is choppy or buffers a lot → [Choppy webcam stream](#choppy-premium)

If the webcam looks fine in Mainsail/Fluidd but is very choppy in Obico, see [Troubleshoot choppy/jerky Premium Streaming](/docs/user-guides/webcam-feed-is-laggy/) — your hardware or OS may not support H.264 encoding. See also [OS compatibility for webcam streaming](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/#4-did-you-use-the-official-octopi-image-to-flash-the-sd-card).

### Step 5: Still stuck?

[Get help from a human](/docs/user-guides/contact-us-for-support). If support asks you to send log files, see how to download them for [Obico for Klipper](/docs/user-guides/moonraker-obico/logging-file/) or [Obico for OctoPrint](/docs/user-guides/turn-on-debug-logging/).

## No webcam in the Obico app {#no-webcam}

:::tip
After you open the Obico mobile app or web app, wait for up to 5 seconds for the webcam stream to load.
:::

By default, Obico will automatically stream the webcam(s) configured in Klipper (Mainsail/Fluidd) or OctoPrint. If there is no webcam stream in the Obico app, check if the webcam stream works correctly in Klipper (Mainsail/Fluidd) or OctoPrint.

If the webcam stream works in Klipper (Mainsail/Fluidd) or OctoPrint, but is missing or a black screen in the Obico app, you may have to manually configure webcam(s) in Obico.

- [Configure webcam in Obico for Klipper](/docs/user-guides/moonraker-obico/webcam/)
- [Configure webcam in Obico for OctoPrint](/docs/user-guides/multiple-cameras-octoprint/)

If you got here from a [Webcam Streaming Failed](#webcam-streaming-failed) notification and the webcam works in Mainsail/Fluidd/OctoPrint, double-check your Obico webcam configuration using the links above.

## Webcam only refreshes once about every 10 seconds (0.1FPS webcam stream) {#0.1-fps}

The most common cause for this problem is that [Janus is not installed on your printer or SBC](/docs/user-guides/webcam-install-janus/). When this is the case, you will also see a warning in the Obico app:

![Janus Not Found](/img/user-guides/helpdocs/janus-not-found-warning.png)

The solution is to install Janus on your printer or SBC. [Follow this guide for details](/docs/user-guides/webcam-install-janus/).

If you are running a self-hosted Obico server, it's also possible that Janus is installed but the WebRTC connection can't be established due to your network configurations (firewall, routing, NAT configuration in your router, etc). To check if this is the case, [re-link your printer to the Obico cloud](/docs/user-guides/relink-printer/). If the issue is gone, the problem is with the settings of your server or its network configuration.

Follow [this guide](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/) for other less common problems that may cause the webcam to stream at only 0.1FPS.

## Webcam stream is choppy {#choppy-premium}

The most common reason why your webcam stream appears choppy is because you don't have an Obico AI Premium subscription.

* You are eligible for the Premium Streaming (25 frames-per-second) if you are currently an AI Premium plan subscriber or in the free 1-month AI Premium trial.
* You are eligible for only the Basic Streaming if you are on the Free plan. In this case, the webcam stream is up to 5 frames-per-second, which can appear to be quite choppy. Also it's throttled for 30 seconds every minute.

Visit [your Obico account subscription page](https://app.obico.io/user_preferences/subscription/) if you are not sure.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

If you already have an AI Premium subscription but your webcam stream is still choppy, follow [this complete troubleshooting guide](/docs/user-guides/webcam-feed-is-laggy/).

## Get help from a human {#get-help}

If your issue is not listed above, or you have exhausted the troubleshooting guide but still can't get the issue resolved, [get help from a human](/docs/user-guides/contact-us-for-support).
