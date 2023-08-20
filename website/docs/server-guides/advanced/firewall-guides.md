---
title: Firewall configuration on Windows, Mac, and Linux
---

:::danger
**Security Warning**: The guide below only cover the basic steps to set up firewall for self-hosted Obico Server. The setup required to properly secure your private network is too complicated to be covered here. Please do your own research to gather the necessary info before you proceed.
:::

:::note
This is a community-contributed guide. This guide is based on certain Obico community members' own setup and hence may not work for you.
:::

## Port/Firewall {#portfirewall}

The Obico Server listens on port 3334.

You can set up a reverse-proxy, such as nginx, in front of the Obico Server, so that it's exposed on a different port. In this case, please use whichever port you choose to expose in the steps below. For simplicity sake, this document assumes the server port is 3334.

## Windows {#windows}

Windows blocks all incoming connections by default. To allow the connection between your server and the octopi, you will need to open TCP port 3334.

1. Right click on the windows icon or use the shortcut Win + X.

2. Choose Windows PowerShell (Admin) from the pop-up menu.

3. Run the following command.

```powershell
New-NetFirewallRule -DisplayName 'Obico' -Name 'Obico' -Description 'inbound rule through TCP port 3334 intended for a private Obico' -direction inbound -action allow -Profile Private -Protocol TCP -LocalPort 3334
```

## Mac {#mac}

Mac comes with a firewall, but it doesn't block incoming connections by default. If you haven't enabled, skip this section.

1. Open System Preferences.

2. Click Security and Privacy

3. Navigate to the Firewall pane

4. Unlock preferences by clicking the lock in the bottom left and signing in as an admin.

5. Click on Firewall Options...

6. Add Docker to the list of allowed applications.

7. Ta-da! Your Obico Server can now talk with other computers/octopies in the network

## Linux {#linux}

Since each distro comes with different firewalls, please refer to the guide for your distro (usually on the distro website).
