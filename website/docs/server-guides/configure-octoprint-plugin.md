---
title: Configure Obico for OctoPrint to use self-hosted server
---

Before you can configure Obico for OctoPrint plugin to use your own server, you need add a printer to The Spaghetti Detective server you just built and obtain the 6-digit Verification Code for that. To do so:

1. Pointing your browser to `http://your_server_ip:3334`.

1. Log in as a user (you can just login with `root@example.com` but it's more secure to use a non-admin user).

1. Add a new printer as described in [this guide](https://www.obico.io/docs/user-guides/octoprint-plugin-setup-manual-link/) and obtain the 6-digit Verification Code. *Note: Do it on your own server, not on [the Obico cloud](https://app.obico.io).*

Then, navigate to octoprint to setup the plugin side of things:

1. Make sure that you have installed the [Obico for OctoPrint plugin](https://www.obico.io/docs/user-guides/octoprint-plugin-setup/).

1. After restarting, go through the wizard as described in [the setup guide](https://www.obico.io/docs/user-guides/octoprint-plugin-setup-manual-link/), until you are at the last step that asks for the 6-digit Verification Code. *Note: If Obico for OctoPrint plugin has been installed before and you do not see the wizard, click [here](https://www.obico.io/docs/user-guides/octoprint-plugin-setup-manual-link/#step-1-launch-the-setup-wizard-in-the-plugin).*

1. Expand "Advanced Server Configuration".  Find and change the Server Address to `http://your_server_ip:3334` (use https:// if you have HTTPS configured, if you aren't sure, just use http://). You MUST include the "http://".

![Change server address](/img/server-guides/Change-Server-Address.png)

1. Enter in your code and octoprint should automatically link to your printer!

1. Give you printer a fancy name and enjoy Obico!
