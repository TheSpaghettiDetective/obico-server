---
id: klipper-setup
title: Set up Obico for Klipper
description: For users using Klipper with Mainsail or Fluidd
sidebar_label: Set up Obico for Klipper
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::caution
 This guide is for the users who use Klipper with Moonraker and **Mainsail or Fluidd**. If you are using OctoPrint with Klipper, please follow the [Obico for OctoPrint guide](octoprint-plugin-setup.md) instead.
:::

:::info
This guide assumes you are connecting to the [Obico Cloud](https://app.obico.io). If you are connecting to a [self-hosted Obico Server](/docs/server-guides/), you will need to use the address of your self-hosted server.
:::

## Hardware requirements {#hardware-requirements}

Before you start, make sure:

- You have set up Klipper and the Moonraker API correctly, and it is connected to your printer. A interface such as Mainsail/Fluidd is highly recommended.
- A webcam is set up for your printer and connected to Mainsail/Fluidd/Moonraker.
- There is sufficient lighting to illuminate the printing area of your printer. If your printer is in a lighted room, you are probably fine. If you'll print with light off, you will need to make sure the printing area is illuminated when your printer is printing. A LED strip or small LED lamp will do the trick.


## Step 1: Download Obico for Klipper and run `install.sh` {#step-1-download-obico-for-klipper-and-run-installsh}

1. Use SSH to connect to the Raspberry Pi your Klipper runs on.
2. Run the following commands one by one:
```bash
    cd ~
    git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
    cd moonraker-obico
    ./install.sh
```
3. Follow the guided installation steps on your screen. You may be asked to enter your password in order to run `sudo` commands.
5. When asked for additional information about configuration files, provide their location or the appropriate number. Default for Klipper may be:
    1. `moonraker.conf` configuration file: `~/printer_data/config/moonraker.conf` or `~/moonraker.conf` (see [Moonraker docs][])
    2. Moonraker network address: The IP or hostname of the Klipper machine
    3. Moonraker network port: `7125` (HTTP) or `7130` (HTTPS) (see [\[server\]][])
    4. Log file directory: `/logs` folder (root level of the disk) (see [moonraker.log])
6. Next, the installation process will ask you to enter details required to link your printer to the Obico server. Provide:
    - The Obico Server you want to link it to. The default is `https://app.obico.io` (the [Obico Cloud](https://app.obico.io)).
      Alternatively, you can also [host your own Obico Server][]: enter the IP address or hostname of your own server (e.g. http://192.168.0.5:3334).
    - A **6-digit verification code**. **Leave the terminal window open on this screen.**
7. Follow the guide outlined in [Step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app) to either link your Klipper machine and Obico automatically, **or** obtain the 6-digit manual verification code.
    - If the automatic linking process is successful, the prompt in the terminal will automatically be skipped.
    - You do not need the 6-digit code if automatic linking can be performed.

[Moonraker docs]: https://moonraker.readthedocs.io/en/latest/configuration/
[\[server\]]: https://moonraker.readthedocs.io/en/latest/configuration/#server
[moonraker.log]: https://moonraker.readthedocs.io/en/latest/web_api/#download-moonrakerlog

[host your own Obico Server]: https://www.obico.io/docs/server-guides/

## Step 2: Sign up for an Obico account. {#step-2-sign-up-for-an-obico-account}

:::tip

Follow instructions in the "**📱  Mobile App**" tab if you are using the Obico mobile app, or the "**🌐  Web App**" tab if you are using the web app.

:::

:::info

Your Obico account is the same for the mobile app and the web app. If you sign up for an account using the mobile app, you can sign in to the web app later with the same email and password. And vice versa.

:::

:::info

All functions are available equally in the mobile and the web app. However, with the mobile app, you can receive push notifications on your phone to easily track the print progress, and get alerted in case a failure is detected.

:::

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Download the Obico app from the [Apple App Store](https://apps.apple.com/us/app/the-spaghetti-detective/id1540646623?ign-itsct=apps_box&ign-itscg=30200) or [Google Play Store](https://play.google.com/store/apps/details?id=com.thespaghettidetective.android).
1. Open the mobile app. Click through the first time tour and then tap **“Let’s Go!”**.
1. Simply tap "**YES!**" on the "Hardware Required" screen.
1. Tap "**Sign Up/Sign In**" button to proceed to the sign up/sign in screen.
1. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account.

:::info
If you are connecting to a self-hosted Obico Server, press the wrench icon (**🔧**) on the top-left corner of the sign-up screen to change the server address.
:::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/mobile-app-signup.gif" /></div>

  </TabItem>
  <TabItem value="web">

1. Open the [Obico Server sign up page](https://app.obico.io/accounts/signup/) in a new browser tab.
1. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account.

![Sign Up Account](/img/user-guides/setupguide/tsd-signup.png)


  </TabItem>
</Tabs>

<br />

## Step 3: Launch the "Link Printer" wizard in the Obico app {#step-3-launch-the-link-printer-wizard-in-the-obico-app}

:::tip

If your phone or computer is one the **the same local network** as your Klipper is, the Obico app can find your Klipper machine automatically. This is the easiest way to link your printer to your Obico account.

:::

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Press "**Link Printer**" button on the welcome screen. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "**Link New Printer**".
2. Choose "**Klipper**" on the next screen.
3. Assuming you have followed the previous steps and installed the plugin, you can simply click the "**Yes, Obico for Klipper is installed**" button.
4. The app will start scanning for the Klipper printer connected to the same local network.
5. If printer is found, simply click the "**Link**" button and the app will do the rest for you.
  :::tip
  **If, however, the app can't find your printer after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/user-guides/klipper-setup-manual-link) to link your printer using a 6-digit code.**
  :::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-mobile.gif" /></div>
6. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
  <TabItem value="web">

1. On the welcome page, click the "**Link Printer**" button.
2. Click "Klipper" on the page that asks you to select a platform.
1. Assuming you have followed the previous steps and run the `install.sh` script, simply press "Next".
4. The app will start scanning for your Klipper connected to the same local network.
5. If your Klipper printer is found, simply click the "**Link**" button and the app will do the rest for you.
  :::tip
  **If, however, the app can't find your Klipper printer after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/user-guides/klipper-setup-manual-link) to link your printer using a 6-digit code.**
  :::
6. On the message dialog, click the "**Link Now**" button. This will open a new browser tab for a few seconds. This new browser tab is needed to finish a "handshake" with your Klipper printer. If the handshake fails, you will need to switch to the [Manual Setup Guide](/docs/user-guides/klipper-setup-manual-link) to link your printer using a 6-digit code.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-web.gif" /></div>
7. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
</Tabs>

## Step 4: Restart the Raspberry Pi.

Once the Raspberry Pi has booted up, you should be able to see your printer and the webcam stream in the Obico app.

## What's next? {#whats-next}

### Check out your printer feed! {#check-out-your-printer-feed}

Press "Go Check Out Printer Feed!" to see everything you care about your printer: the webcam feed, heater temperature, time remaining on the print job, and more! Remember, you can see your printer feed anywhere you go, as long as you have an internet connection on your phone!

### Test the magical failure detection! {#test-the-magical-failure-detection}

The Detective sounds too magical to be true? [See The Detective in action for yourself](/docs/user-guides/how-to-test-failure-detection).

### Change printer settings. {#change-printer-settings}

The default settings for your printer in The Spaghetti Detective are the ones that most users find the most reasonable. But feel free to tweak them to your liking:

- [Change notification settings](/docs/user-guides/notification-settings) (mobile app only). By default you receive push notifications when The Detective finds something fishy, and for the status of whatever your printer is printing. But you can choose to receive a lot more.
- [Change printer settings](/docs/user-guides/detection-print-job-settings), such as if The Detective should pause your printer when a failure is detected.
