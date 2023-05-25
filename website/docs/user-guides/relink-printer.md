---
title: Re-link printer to Obico server
---

## Why would you re-link your printer? {#why-would-you-re-link-your-printer}

Consider re-linking in one of the following cases:

* [The authentication token is being used by multiple printers](/docs/user-guides/warnings/shared-auth-token-error/).
* You accidentally deleted a printer in the Obico app.
* Your printer is always showing "**offline**" in the app, and you have gone through [all the trouble-shooting steps](/docs/user-guides/troubleshoot-server-connection-issues).
* You don't remember the password of your old the Obico account so you have to sign up for a new account. Now you want to re-link your printer to the new account.

## How to re-link? {#how-to-re-link}

### Obico for OctoPrint

Follow [this guide](/docs/user-guides/octoprint-plugin-setup-manual-link/) to re-link OctoPrint-based printer.

:::note
Your printer can't be automatically identified during the re-linking process. 6-digit code is required to re-link your printer.
:::

### Obico for Klipper

Follow [this guide](/docs/user-guides/relink-klipper/) to re-link Klipper-based printer.