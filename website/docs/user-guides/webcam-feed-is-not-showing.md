---
id: webcam-feed-is-not-showing
title: Troubleshoot the webcam streaming issues
---

Follow this guide if you are experiencing any of these webcam streaming issues:

* Webcam stream is stuck (buffering), or video frames dropped.
* Choppy/jerky webcam stream.
* No webcam stream at all.

## 1. Determine if you are eligible for the Premium Streaming {#1-determine-if-you-are-eligible-for-the-premium-streaming}

* You are eligible for the Premium Streaming (25 frames-per-second) if you are currently a Pro plan subscriber or in the free 1-month Pro trial.
* You are eligible for only the Basic Streaming if you are on the Free plan. In this case, the webcam stream is up to 5 frames-per-second. Also it's throttled for 30 seconds every minutes.

If you are not sure, [follow this guide](/docs/user-guides/check-type-of-your-account) to find out if you are currently on a Free plan or a Pro plan.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

## 2. Check the current streaming mode {#2-check-the-current-streaming-mode}

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to find out the current webcam streaming mode.

* If you are eligible for the Premium Streaming, the streaming mode should be "**Premium (advanced)**" or "**Premium (compatibility)**".
* If you are eligible for the Premium Streaming, the streaming mode should be "**Basic**".

If the streaming mode is "**0.1 FPS**", [follow this troubleshooting guide](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/).

## 3. Check if you get any stream at all {#3-check-if-you-get-any-stream-at-all}

After you open the Obico mobile app or web app, wait for up to 5 seconds for the webcam live stream to load.

![](/img/user-guides/helpdocs/webcam-streaming-not-showing.png)

If the webcam stream is coming in (left in the screenshot above) but the stream is choppy/jerky, [follow this guide](/docs/user-guides/webcam-feed-is-laggy) to fix it.

If you don't see any webcam stream (right), continue to the next step.

## 4. Check for server connection issues {#4-check-for-server-connection-issues}

Server connection issues are the most common root causes for not having a webcam stream. [Follow this troubleshooting guide](/docs/user-guides/troubleshoot-server-connection-issues) to check if it's the case, and if it is, how to fix it.

## 5. Open the troubleshooting page. {#5-open-the-troubleshooting-page}

The Obico plugin has a powerful troubleshooting page to help you diagnose the webcam streaming problems.

You can access this troubleshooting page by:

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click "Obico for OctoPrint" tab.
1. Click the "Troubleshooting" button.

![](/img/user-guides/helpdocs/open-troubleshooting-page.gif)


## 6. Examine connection status on the troubleshooting page {#6-examine-connection-status-on-the-troubleshooting-page}

In the "Plugin Status" column, look for:

* The "Connection to server" status, and
* The "Connection to webcam" statuses

### 6.1 If the server connection has issues {#61-if-the-server-connection-has-issues}

When the plugin has problems connecting to the Obico server, the webcam stream won't come through either.

Follow [this guide](/docs/user-guides/troubleshoot-server-connection-issues) to fix the server connection problem first. Come back to this guide if the webcam streaming still doesn't work after the server connection problem is fixed.

:::note
You can still get a decent webcam stream even if there are occasional server connection errors, e.g., the error rate is lower than 5%.
:::

### 6.2 If the webcam connection shows "Error" {#62-if-the-webcam-connection-shows-error}

This usually means the webcam streaming in OctoPrint is not working. [Follow this troubleshoot guide](/docs/user-guides/octoprint-webcam-not-streaming/) to figure out why and fix it.

## 7. None of the above solves the problem? {#7-none-of-the-above-solves-the-problem}

[Get help from a human](/docs/user-guides/contact-us-for-support).
