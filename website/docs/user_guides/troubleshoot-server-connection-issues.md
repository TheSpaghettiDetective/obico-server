---
id: troubleshoot-server-connection-issues
title: Troubleshoot server connection issues
sidebar_label: Troubleshoot server connection issues
---

Server connection issues may be caused by:

* OctoPrint doesn't have a reliable internet connection.
* OctoPrint is not properly linked (paired) to your The Spaghetti Detective account.

:::info

The Spaghetti Detective consists of 2 parts:

* A plugin that runs inside your OctoPrint.
* The Spaghetti Detective server that runs in the cloud (or on your PC if you are running a private server).

The Spaghetti Detective won't work properly when the plugin can't connect to The Spaghetti Detective server.

:::

The Spaghetti Detective plugin provides a powerful set of tools to help you troubleshoot server connection issues.

## 1. Open the troubleshooting page.

1. Open OctoPrint settings page by clicking the wrench icon.
1. Scroll down the navigation bar on the left side.
1. Click "Access Anywhere - The Spaghetti Detective" tab.
1. Click the "Troubleshooting" button.

![](/img/user_guides/helpdocs/open-troubleshooting-page.gif)

## 2. Test server connection by pressing this big fat "TEST" button.

![](/img/user_guides/helpdocs/tsd-plugin-test-connnection.png)

Based on what the test result shows, click one of the following links to continue troubleshooting:

* [<span className="text--danger">Failed to contact server</span>](#21-if-the-test-result-is-failed-to-contact-server)
* [<span className="text--danger">Invalid account credentials</span>](#22-if-the-test-result-is-invalid-account-credentials)
* [<span className="text--success">Succeeded</span>](#23-if-the-test-result-is-succeeded)

### 2.1 If the test result is "<span className="text--danger">Failed to contact server</span>":

![](/img/user_guides/helpdocs/tsd-plugin-failed-to-connect.png)

Most likely, this error means the plugin is configured to point to the wrong server address. To check it:

1. Open OctoPrint settings page by clicking the wrench icon.
2. Scroll down the navigation bar on the left side.
3. Click "Access Anywhere - The Spaghetti Detective" tab.
4. Click the "Settings" button.

![](/img/user_guides/helpdocs/tsd-plugin-open-settings-page.gif)

5. Check server address setting

![](/img/user_guides/helpdocs/tsd-plugin-server-address.png)

Make sure the "**Server Address**" field is:

`https://app.thespaghettidetective.com`

If it is not, please

1. Click the "**Restore Default**" button to set it back.
2. Click the "**Save**" button next to it.
3. **Restart OctoPrint. The change won't take effect until the OctoPrint has been restarted.**

:::note
If you are running your own The Spaghetti Detective server, this field needs to be set to the one of your private server.
:::

If the server address is correct, and you still have server connection error, most likely the OctoPrint has issues with its Internet connection.

### 2.2 If the test result is "<span className="text--danger">Invalid account credentials</span>":

![](/img/user_guides/helpdocs/tsd-plugin-invalid-credential.png)

When you [set up The Spaghetti Detective plugin for the first time](/docs/octoprint-plugin-setup), account credentials were established so that the plugin can connect to the server securely.

There are a few reasons why account credentials would become invalid later on:

* You deleted the printer in The Spaghetti Detective mobile app or web app.
* Some of your printers are "archived" because you have more printers than what your subscription plan allows for.
* You duplicated the OctoPrint SD card to run on anther Raspberry Pi, and duplicated the credentials in the process. When the server detects one set of credentials is being used by multiple printers, it will immediately blacklist the credentials because this usually indicates a security breach.


#### 2.2.1 What if I deleted a printer by mistake

The Detective doesn't make mistakes since she is a robot. But we humans do. 😜

So don't feel bad if you deleted your printer in The Spaghetti Detective by mistake.

We have made it super easy for you to [re-link your OctoPrint to your The Spaghetti Detective account](/docs/octoprint-plugin-setup-manual-link) in less than 2 minutes.

#### 2.2.2 What if my printer was archived

[Unarchive your printer](/docs/unarchive-printer).

:::info
When a printer is "archived", it isn't deleted from the system. You can "unarchive" the printer when you bump up your subscription to the right number of printers.
:::

:::info
If you have a Free plan and you have added a 2nd printer, your 1st printer will be archived within the next 24 hours.
:::

#### 2.2.3 I don't know what happened

If the plugin troubleshooting page shows "invalid account credentials", and you are not sure what is causing the problem, the easiest way to solve this problem is to [re-link OctoPrint for that printer](/docs/octoprint-plugin-setup-manual-link).

#### 2.2.4 Still getting "<span className="text--danger">Invalid account credentials</span>" after re-linking OctoPrint?

Something weird is going on. You will need to [get help from a human](/docs/contact-us-for-support).

### 2.3 If the test result is "<span className="text--success">Succeeded</span>":

![](/img/user_guides/helpdocs/tsd-plugin-succeeded.png)

If the server test button shows "succeeded" but you still experience server connection issues, continue to the next step to check the detailed server connection status.

## 3. Check the detailed server connection status

Find the "**Connection to server**" row in the "**Plugin Status**" column.

![](/img/user_guides/helpdocs/tsd-plugin-troubleshooting-status.jpg)

Based on what the status shows, click one of the following links to continue troubleshooting:

* [<span className="text--success">Okay</span>](#31-if-the-connection-status-is-okay)
* [<span className="text--danger">Disconnect</span>](#32-if-the-connection-status-is-disconnect)
* [<span className="text--danger">Error</span>](#21-if-the-test-result-is-failed-to-contact-server)

### 3.1 If the connection status is "<span className="text--success">Okay</span>":

Hmm, you got us. It looks like you are experiencing a problem the plugin's self-diagnostic tool failed to detect.

When robots failed, [humans will pitch in to help](/docs/contact-us-for-support).

:::info
The Detective's speciality is in detecting spaghetti, not connection problems. Just saying...
:::

### 3.2 If the connection status is "<span className="text--danger">Disconnect</span>":

If the server test button shows "succeeded" but the "Connection to sever" row indicates "Disconnected", it is possible that you have run into a rare situation when the HTTP connection works, but the WebSocket connection doesn't.

The cause for this rare situation can be complicated. A common one is some firewalls would block WebSocket connection but allow HTTP connection to the same port.

This is probably a situation in which you will have fun with your "Google-fu". However, if Google fails to come to the rescue, you can [get help from a human in the TSD community](/docs/contact-us-for-support).

:::info
The plugin connects to the server via 2 connections: HTTP and WebSocket. 99% of the time when one connection works, so will the other. But there are rare situations when HTTP connection works but the WebSocket connection doesn't.
:::

### 3.3 If the connection status is "<span className="text--danger">Error</span>":

When the status is "<span className="text--danger">Connection to server: Error</span>", it usually means your Raspberry Pi has an unreliable Internet connection. The problems can range from very occasional server glitches that doesn't affect the app at all, to a weak Wi-Fi signal strength that results in 50+% loss of network packets and an unusable app.

Fortunately, The Spaghetti Detective plugin provides an diagnostic page that can help you further understand the severity of the server connection problem.

1. Click the "<span className="text--danger">Connection to server: Error</span>" link to open the diagnostic page.
![](/img/user_guides/helpdocs/tsd-plugin-server-connection-error.jpg)
2. [Find out the severity of the connectivity issue and the possible solution](/docs/connectivity-error-report#how-to-assess-the-server-connectivity-issues).

## None of the above solves the problem?

[Get help from a human](/docs/contact-us-for-support).