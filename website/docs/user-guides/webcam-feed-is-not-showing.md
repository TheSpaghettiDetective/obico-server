---
id: webcam-feed-is-not-showing
title: Troubleshoot the webcam streaming issues
---

Follow this guide if you are experiencing any of these webcam streaming issues:

* Webcam stream is stuck (buffering), or video frames dropped.
* Choppy/jerky webcam stream.
* No webcam stream at all.

## Determine if you are eligible for the Premium Webcam Streaming

* You are eligible for the Premium Streaming (25 frames-per-second) if you are currently a Pro plan subscriber or in the free 1-month Pro trial. Follow the ["Troubleshoot the Premium Streaming issues"](#troubleshoot-the-premium-streaming-issues) section if it's the case.
* You are eligible for only the Basic Streaming if you are on the Free plan. If so, follow the ["Troubleshoot the Basic Streaming issues"](#troubleshoot-the-basic-streaming-issues) section.

If you are not sure, [follow this guide](/docs/user-guides/check-type-of-your-account) to find out if you are currently on a Free plan or a Pro plan.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

## Troubleshoot the Premium Streaming issues

Follow the steps below if you are eligible for the Premium Streaming.

### 1. Check if the streaming is stuck in the "**Basic**" mode

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode) to find out the current webcam streaming mode.

The streaming mode should be "**Premium (advanced)**" or "**Premium (compatibility)**". If the streaming mode is stuck in "**Basic**", [follow this troubleshooting guide](/docs/user-guides/premium-streaming-stuck-in-basic-mode/).

### 2. Check if you get any stream at all

After you open The Spaghetti Detective mobile app or web app, wait for up to 5 seconds for the webcam live stream to load.

![](/img/user-guides/helpdocs/webcam-streaming-not-showing.png)

If the webcam stream is coming in (left in the screenshot above) but the stream is choppy/jerky, [follow this guide](/docs/user-guides/webcam-feed-is-laggy) to fix it.

If you don't see any webcam stream (right), continue to the next step.

### 3. Check for server connection issues

Server connection issues are the most common root causes for not having a webcam stream. [Follow this troubleshooting guide](/docs/user-guides/troubleshoot-server-connection-issues) to check if it's the case, and if it is, how to fix it.

### 4. Try "always stream in compatibility mode"

Try to [set the compatibility mode set to "**always**"](/docs/user-guides/streaming-compatibility-mode#how-to-change-the-compatibility-mode-setting). **You need to restart the Raspberry Pi**.


### 5. None of the above solves the problem?

[Get help from a human](/docs/user-guides/contact-us-for-support).

## Troubleshoot the Basic Streaming issues

Follow the steps below if you are only eligible for the Basic Streaming.

### 1. Is your 3D printer currently printing?

The Basic Streaming is activated only when your 3D printer is printing.

If your 3D printer is not printing right now, please start a test print. After about 30 seconds, check if you are getting the webcam stream in The Spaghetti Detective app now.

If the webcam stream still doesn't come up, continue to the next step of this guide.


### 2. Open the troubleshooting page.

The Spaghetti Detective plugin has a powerful troubleshooting page to help you diagnose the webcam streaming problems.

You can access this troubleshooting page by:

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click "Access Anywhere - The Spaghetti Detective" tab.
1. Click the "Troubleshooting" button.

![](/img/user-guides/helpdocs/open-troubleshooting-page.gif)


### 3. Examine connection status on the troubleshooting page

In the "Plugin Status" column, look for:

* The "Connection to server" status, and
* The "Connection to webcam" statuses

#### 3.1 If the server connection has issues

When the plugin has problems connecting to The Spaghetti Detective server, the webcam stream won't come through either.

Follow [this guide](/docs/user-guides/troubleshoot-server-connection-issues) to fix the server connection problem first. Come back to this guide if the webcam streaming still doesn't work after the server connection problem is fixed.

:::note
You can still get a decent webcam stream even if there are occasional server connection errors, e.g., the error rate is lower than 5%.
:::

#### 3.2 If the webcam connection shows "Error"

This usually means the webcam streaming in OctoPrint is not working. [Follow this troubleshoot guide](/docs/user-guides/octoprint-webcam-not-streaming/) to figure out why and fix it.

### 4. None of the above solves the problem?

[Get help from a human](/docs/user-guides/contact-us-for-support).