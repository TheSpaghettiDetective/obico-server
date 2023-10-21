---
title: Re-link printer to Obico server
---

## Why would you re-link your printer? {#why-would-you-re-link-your-printer}

Consider re-linking in one of the following cases:

* You accidentally deleted a printer in the Obico app.
* Your printer is always showing "**offline**" in the app, and you have gone through [all the trouble-shooting steps](/docs/user-guides/troubleshoot-server-connection-issues).
* You don't remember the password of your old the Obico account so you have to sign up for a new account. Now you want to re-link your printer to the new account.
* [The authentication token is being used by multiple printers](/docs/user-guides/warnings/shared-auth-token-error/).
* You want to switch from the Obico cloud to your own self-hosted Obico server, or the other way around.

## How to re-link? {#how-to-re-link}

:::note
Your printer can't be automatically identified during the re-linking process. 6-digit code is required to re-link your printer.
:::

### Obico for OctoPrint {#obico-for-octoprint}

Follow [this guide](/docs/user-guides/octoprint-plugin-setup-manual-link/) to re-link OctoPrint-based printer.

### Obico for Klipper {#obico-for-klipper}

Follow [this guide](/docs/user-guides/klipper-setup-manual-link/) to re-link Klipper-based printer.