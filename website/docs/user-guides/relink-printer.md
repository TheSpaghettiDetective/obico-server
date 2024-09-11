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

:::caution
If you are switching from self-hosted Obico server to the Obico cloud, or the other way around, you need to change the server address both in the Obico app and on your printer/Raspberry Pi.
:::

### (Optionally) Change the Obico server address in the Obico app

1. If you have logged in the Obico app, log out first.
2. Click the wrench icon (**🔧**) located at the top-left corner of the screen.
3. On the next screen, enter the server address, and press "Set & Relaunch". Or if you want to switch to using the Obico app, simply press "Reset to Obico Cloud".
4. After the app restarts, login with the correct credential.

![](/img/user-guides/helpdocs/change_obico_server_app.png)


### Re-link Obico for Klipper {#obico-for-klipper}

1. (Optionally) Follow [this guide](/docs/user-guides/moonraker-obico/config/) to change the `url` configuration in the `[server]` section inside `moonraker-obico.cfg`.
1. Follow [this guide](/docs/user-guides/klipper-setup-manual-link/) to re-link Klipper-based printer.

### Re-link Obico for OctoPrint {#obico-for-octoprint}

1. (Optionally) Change the Obico server address in Obico for OctoPrint.

![](/img/user-guides/helpdocs/change_obico_server_address_octoprint.png)

2. Follow [this guide](/docs/user-guides/octoprint-plugin-setup-manual-link/) to re-link OctoPrint-based printer.
