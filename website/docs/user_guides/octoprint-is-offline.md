---
id: octoprint-is-offline
title: Why is OctoPrint showing as "offline"?
---

If you are sure OctoPrint is powered on, but it is showing as "offline", follow these steps to figure out why.

## Step 1: Make sure your token is configured correctly.

1. Open OctoPrint page (not The Spaghetti Detective page). Open "Settings" by clicking the wrench icon.
1. Scroll the sidebar to the bottom and click "Access Anywhere - The Spaghetti Detective".
1. Make sure the secret token in the box is set correctly. If you are not sure how to get this secret token, you can find it in [Getting Started](/docs/user_guides/octoprint-plugin-setup/).
1. Click "Test" button.
1. Make sure you see "<span style={{color: "#468847"}}>Secret token is valid. You are awesome.</span>" (because you are).
1. If the secret token is tested Ok, but The Spaghetti Detective page is still showing "OctoPrint is offline", move on to Step 2.

![Token verified](/img/user_guides/verified-token.png)

## Step 2: Check the plugin's connection to The Spaghetti Detective server.

Your OctoPrint needs to have a good internet connection in order for the plugin to send webcam feed and print job status to The Spaghetti Detective server. To verify that:

1. On "Access Anywhere - The Spaghetti Detective" settings page in OctoPrint (see Step 1), click "Got problems?".
1. Click the "Check plugin self diagnostic report >>>" link.
1. If there are no connection problems, you should see "<span style={{color: "#468847"}}>There have been no connection errors since OctoPrint rebooted.</span>".

![Connection Verified](/img/user_guides/verified-connection.png)

4. If, instead, you see these error messages, your OctoPrint has had issues to connect to The Spaghetti Detective server. Most likely it's because the Raspberry Pi (or whatever computer your OctoPrint runs on) has not had reliable internet connection.

![Connection problems](/img/user_guides/server-connection-error.png)

## Step 3: Turn on debug logging and look for the needle in the haystack.

Turn on debug logging and download `octoprint.log` file ([here is how](/docs/user_guides/turn-on-debug-logging)). Open `octoprint.log` file with your favorite editor and look for errors.

## Step 4: If all tests in the previous steps passed but it still shows "OctoPrint is offline", [reach out to us for help](/docs/user_guides/contact-us-for-support).
