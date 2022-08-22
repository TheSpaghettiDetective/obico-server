---
id: octoprint-plugin-setup
title: Set up Obico for OctoPrint
description: For OctoPrint users
sidebar_label: Set up Obico for OctoPrint
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::info
This guide assumes you are connecting to the [Obico Cloud](https://app.obico.io). If you are connecting to a [self-hosted Obico Server](/docs/server-guides/), you will need to use the address of your self-hosted server.
:::

## Hardware requirements {#hardware-requirements}

Before you start, make sure:

- OctoPrint is installed and set up correctly. The easiest way to set up OctoPrint is to get a Raspberry Pi and follow [this guide](https://octoprint.org/download/).
- A webcam is set up for your printer and connected to OctoPrint. The 3D Printing Zone has an [excellent video](https://www.youtube.com/watch?v=uWsD2HoId9I) for it.
- There is sufficient lighting to illuminate the printing area of your printer. If your printer is in a lighted room, you are probably fine. If you'll print with light off, you will need to make sure the printing area is illuminated when your printer is printing. A LED strip or small LED lamp will do the trick.


## Step 1: Install "Obico for OctoPrint" plugin. {#step-1-install-obico-for-octoprint-plugin}

1. Open OctoPrint page in a browser.
1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. On the settings page, click "**Plugin Manager**", then "**Get More...**".
1. Type "Obico" in the box, you will see "Obico for OctoPrint" plugin.
1. Click "**Install**".
1. Click "**Restart Now**" when OctoPrint asks.

![Install the Plugin](/img/user-guides/setupguide/install-plugin.png)

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
  defaultValue="mobile"
  groupId="app"
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

If you are phone or computer is one the **the same local network** as your OctoPrint is, the Obico app can find your OctoPrint automatically. This is the easiest way to link printer to your Obico account.

:::

<Tabs
  defaultValue="mobile"
  groupId="app"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Press "**Link Printer**" button on the welcome screen. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "**Link New Printer**".
2. Choose "**OctoPrint**" on the next screen.
3. Assuming you have followed the previous steps and installed the plugin, you can simply click the "**Yes, plugin is installed**" button.
4. The app will start scanning for the OctoPrint connected to the same local network.
5. If the OctoPrint is found, simply click the "**Link**" button and the app will do the rest for you.
  :::tip
  **If, however, the app can't find your OctoPrint after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/user-guides/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.**
  :::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-mobile.gif" /></div>
6. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
  <TabItem value="web">

1. On the welcome page, click the "**Link Printer**" button.
2. Click "OctoPrint" on the page that asks you to select a platform.
3. Assuming you have followed the previous steps and installed the plugin, you can simply click the "**Next**" button.
4. The app will start scanning for the OctoPrint connected to the same local network.
5. If the OctoPrint is found, simply click the "**Link**" button and the app will do the rest for you.
  :::tip
  **If, however, the app can't find your OctoPrint after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/user-guides/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.**
  :::
6. On the message dialog, click the "**Link Now**" button. This will open a new browser tab for a few seconds. This new browser tab is needed to finish a "handshake" with your OctoPrint. If the handshake fails, you will need to switch to the [Manual Setup Guide](/docs/user-guides/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-web.gif" /></div>
7. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
</Tabs>

<b />

## What's next? {#whats-next}

### Check out your printer feed! {#check-out-your-printer-feed}

Press "Go Check Out Printer Feed!" to see everything you care about your printer: the webcam feed, heater temperature, time remaining on the print job, and more! Remember, you can see your printer feed anywhere you go, as long as you have an internet connection on your phone!

### Test the magical failure detection! {#test-the-magical-failure-detection}

AI-powered failure detection sounds too magical to be true? [See the magic in action for yourself](/docs/user-guides/how-to-test-failure-detection).

### Change printer settings. {#change-printer-settings}

The default settings for your printer in Obico are the ones that most users find the most reasonable. But feel free to tweak them to your liking:

- [Change notification settings](/docs/user-guides/notification-settings) (mobile app only). By default you receive push notifications when a possible print failure is detected. You will also get status update on your lock screen when your printer is printing. But you can choose to receive a lot more.
- [Change printer settings](/docs/user-guides/detection-print-job-settings), such as if Obico should pause your printer when a failure is detected.
