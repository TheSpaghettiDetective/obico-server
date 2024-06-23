---
title: Manually Link Klipper with a 6-digit code
description: For Klipper/Moonraker/Mainsail/Fluidd users
sidebar_label: Manually Link Klipper
---

:::caution
  **If you are on Obico for Klipper version than 1.6.0 or newer, switch to [Updated Manual Setup Guide](https://www.obico.io/docs/user-guides/klipper-setup/#link-manually) to link your printer using a one-time passcode.**
:::

Follow this guide in one of these 2 rare cases:

* You are trying to re-link your Klipper printer. There are only [a few reasons](/docs/user-guides/relink-printer/) why you need to re-link printer.
* Your printer can't be identified at the last step in [Obico for Klipper setup guide](/docs/user-guides/klipper-setup/). You don't need a 6-digit code if your printer can be identified and linked automatically.

:::caution
If you are setting up Obico for the first time, you should follow [Obico for Klipper setup guide](/docs/user-guides/klipper-setup) first. **Please DO NOT PROCEED** if you haven't done so.
:::


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::caution
 This guide is for the users who use **Moonraker with Klipper**. If you are using OctoPrint with Klipper, please follow the [Obico for OctoPrint guide](octoprint-plugin-setup.md) instead.
:::

:::info
This guide assumes you are connecting to the [Obico Cloud](https://app.obico.io). If you are connecting to a [self-hosted Obico Server](/docs/server-guides/), you will need to use the address of your self-hosted server.
:::


## Step 1: Download Obico for Klipper and run `install.sh` {#step-1-download-obico-for-klipper-and-run-installsh}

1. SSH to the Raspberry Pi (or other SBC) your Klipper runs on.
2. Run:
```bash
    cd ~
    git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
    cd moonraker-obico
    ./install.sh
```
3. Follow the installation steps. You may be asked to enter the password in order to run `sudo` commands.
5. You will also be asked to enter the configurations necessary for the installation to complete, such as the location of your `moonraker.conf`, Moonraker's port and address, and the log directory.
6. `install.sh` will now start the process to link your printer to the Obico server. You will be asked to enter:
    - The Obico Server you want to link it to. The default is the [Obico Cloud](https://app.obico.io). You can also change it to using your own [self-hosted Obico Server](https://www.obico.io/docs/server-guides/) (ex: http://192.168.0.5:3334).
    - A **6-digit verification code**. You will obtain this 6-digit verification code in the following steps.
7. Leave the terminal open. We will come back to enter the 6-digit code once we obtain it from the Obico app.

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

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

Press "**Link Printer**" button on the welcome screen. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "**Link New Printer**".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/launch-manual-link-mobile.jpg" /></div>

  </TabItem>
  <TabItem value="web">

On the welcome page, click the "**Link Printer**" button.

![Welcome page](/img/user-guides/setupguide/welcome-web.jpg)

  </TabItem>
</Tabs>

## Step 4: Obtain the 6-digit verification code {#step-4-obtain-the-6-digit-verification-code}

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Choose "**Klipper**" on the next screen.
1. Assuming you have followed the previous steps and run the `install.sh` script, simply press "**Yes. Obico for Klipper is installed**".
1. Now you will see a screen with a 6-digit verification code. This is the code you will use to link your printer. You can long-press the number to copy it to the clipboard.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/klipper-verification-code-mobile.jpg" /></div>

<div />

  </TabItem>

  <TabItem value="web">

1. Click "Klipper" on the page that asks you to select a platform.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/select-platform-web.jpg" /></div>

2. Assuming you have followed Step 1 and run the `install.sh` script, you can simply click the "**Next>**" button.
3. Now you will see a screen with a 6-digit verification code. You can press Ctrl-C (Windows) or Cmd-C (Mac) to copy the 6 digit code to the clipboard.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/klipper-verification-code-web.jpg" /></div>

  </TabItem>
</Tabs>

## Step 5: Enter the 6-digit code {#step-5-enter-the-6-digit-code}

1. Go back to terminal for your SSH session in Step 1.
1. Enter the 6-digit code you obtained in the previous step.
1. As the final step, you will be asked if you want to opt in bug reporting. We strongly recommend you answer "Y" here. Bug reporting will help us catch and fix bugs earlier and more easily, and hence a better Obico app for you! :)

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/link-success-klipper.png" /></div>
<br />

## Step 6: Restart the Raspberry Pi. {#step-6-restart-the-raspberry-pi}

Once the Raspberry Pi has booted up, you should be able to see your printer and the webcam stream in the Obico app.

## Step 7 (optional): Give your printer a shiny name! {#step-6-optional-give-your-printer-a-shiny-name}

Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".
