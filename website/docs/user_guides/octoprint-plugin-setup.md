---
id: octoprint-plugin-setup
title: Set up The Spaghetti Detective in 56 seconds
sidebar_label: Getting started in 56 seconds
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Setting up The Spaghetti Detective is super simple. There is a good chance you can get it all set up in 56 seconds (start your stop watch now!). If you prefer, you can also follow [this video guide](https://youtu.be/l2yMySAxIKw) that covers the same setup process.
 
## Hardware requirements

Before you start, make sure:

- OctoPrint is installed and set up correctly. The easiest way to set up OctoPrint is to get a Raspberry Pi and follow [this guide](https://octoprint.org/download/).
- A webcam is set up for your printer and connected to OctoPrint. The 3D Printing Zone has an [excellent video](https://www.youtube.com/watch?v=uWsD2HoId9I) for it.
- There is sufficient lighting to illuminate the printing area of your printer. If your printer is in a lighted room, you are probably fine. If you'll print with light off, you will need to make sure the printing area is illuminated when your printer is printing. A LED strip or small LED lamp will do the trick.


## Step 1: Install "Access Anywhere - The Spaghetti Detective" plugin in OctoPrint.

:::note

If you have purchased a hardware kit with OctoPrint and The Spaghetti Detective plugin pre-installed, skip this step and jump to [Step 2](#step-2-sign-up-for-a-the-spaghetti-detective-account).

:::

1. Open OctoPrint page in a browser.
1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. On the settings page, click "**Plugin Manager**", then "**Get More...**".
1. Type "The Spaghetti Detective" in the box, you will see "**Access Anywhere - The Spaghetti Detective**" plugin.
1. Click "**Install**".
1. Click "**Restart Now**" when OctoPrint asks.

![Install the Plugin](/img/user_guides/setupguide/tsd-plugin-install.gif)

## Step 2: Sign up for a The Spaghetti Detective account.

:::tip

Follow instructions in the "**📱  Mobile App**" tab if you are using The Spaghetti Detective mobile app, or the "**🌐  Web App**" tab if you are using the web app.

:::

:::info

Your The Spaghetti Detective account is the same for the mobile app and the web app. If you sign up for an account using the mobile app, you can sign in to the web app later with the same email and password. And vice versa.

:::

:::info

All The Spaghetti Detective functions are available equally in the mobile and the web app. However, with the mobile app, you can receive push notifications on your phone for events like detected print failures or the end of a print job.

:::

<Tabs
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Download The Spaghetti Detective app from the [Apple App Store](https://apps.apple.com/us/app/the-spaghetti-detective/id1540646623?ign-itsct=apps_box&ign-itscg=30200) or [Google Play Store](https://play.google.com/store/apps/details?id=com.thespaghettidetective.android).
1. Open the mobile app. Click through the first time tour and then tap **“Let’s Go!”**.
1. Simply tap "**YES!**" on the "Hardware Required" screen.
1. Tap "**Sign Up/Sign In**" button to proceed to the sign up/sign in screen.
1. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account. 

<br />

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user_guides/setupguide/mobile-app-signup.gif" /></div>

  </TabItem>
  <TabItem value="web">

1. Open [The Spaghetti Detective sign up page](https://app.thespaghettidetective.com/accounts/signup/) in a new browser tab.
1. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account. 

![Sign Up Account](/img/user_guides/setupguide/tsd-signup.png)


  </TabItem>
</Tabs>

<br />

## Step 3: Link OctoPrint to your The Spaghetti Detective account.

:::tip

Connect OctoPrint to **the same local network** as your phone or computer. The Spaghetti Detective app can find your OctoPrint automatically. This is the easiest way to link OctoPrint to your The Spaghetti Detective account.

:::

<Tabs
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Click "**Link OctoPrint**" button.
2. Assuming you have followed the previous steps and installed the plugin, you can simply click the "**Yes, plugin is installed**" button.
3. The app will start scanning for the OctoPrint connected to the same local network. 
4. If the OctoPrint is found, simply click the "**Link**" button and the app will do the rest for you.
  :::note
  **If, however, the app can't find your OctoPrint after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.**
  :::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user_guides/setupguide/auto-link-mobile.gif" /></div>
<br />

5. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user_guides/setupguide/link-success-mobile.gif" /></div>

  </TabItem>
  <TabItem value="web">

1. Click "**Link OctoPrint**" button.
2. Assuming you have followed the previous steps and installed the plugin, you can simply click the "**Next**" button.
3. The app will start scanning for the OctoPrint connected to the same local network. 
4. If the OctoPrint is found, simply click the "**Link**" button and the app will do the rest for you.
  :::note
  **If, however, the app can't find your OctoPrint after 1 minute of scanning, you need to follow the [Manual Setup Guide](/docs/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.**
  :::
5. On the message dialog, click the "**Link Now**" button. This will open a new browser tab for a few seconds. This new browser tab is needed to finish a "handshake" with your OctoPrint. If the handshake fails, you will need to switch to the [Manual Setup Guide](/docs/octoprint-plugin-setup-manual-link) to link your OctoPrint using a 6-digit code.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user_guides/setupguide/auto-link-web.gif" /></div>
<br />

6. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user_guides/setupguide/link-success-web.gif" /></div>

  </TabItem>
</Tabs>

<b />

## Step 4: There is no step 4. It is this simple.

You are done! Hope it didn't take more than 56 seconds. :)

The Detective will now watch your prints and send you alerts when things go awry. Start printing and enjoying the peace of the mind.

## What's next?

### Check out your printer feed!

Press "Go Check Out Printer Feed!" to see everything you care about your printer: the webcam feed, heater temperature, time remaining on the print job, and more! Remember, you can see your printer feed anywhere you go, as long as you have an internet connection on your phone!

### Test the magical failure detection!

The Detective sounds too magical to be true? [See The Detective in action for yourself](/docs/how-to-test-failure-detection).

### Change printer settings.

The default settings for your printer in The Spaghetti Detective are the ones that most users find the most reasonable. But feel free to tweak them to your liking:

- [Change notification settings](/docs/notification-settings) (mobile app only). By default you receive push notifications when The Detective finds something fishy, and for the status of whatever your printer is printing. But you can choose to receive a lot more.
- [Change printer settings](/docs/detection-print-job-settings), such as if The Detective should pause your printer when a failure is detected.
