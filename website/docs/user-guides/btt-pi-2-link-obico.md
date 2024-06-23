---
id: btt-pi-2-link-obico
title: Setup Obico on BTT Pi 2
sidebar_label: Obico BTT Pi 2 Setup 
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/btt-pi-2-guide/btt_x_obico_dark.png" /></div>


This guide will show you how to link Obico on your [BigTreeTech Pi 2](https://biqu.equipment/products/bigtreetech-x-obico-bigtreetech-pi-2-ai). Thanks to the collaboration between BTT and Obico, Obico's software is pre-installed on the BTT Pi 2 giving all users access to AI failure detection and remote 3d printer access. 

Link your printer to get access to webcam streaming, print status and failure notifications, 3D printer monitoring/control and more all from your phone.

:::note
If you prefer the video format over a text-based guide, we have also prepared this video tutorial.
:::

<div className="videoWrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/sUIAhyZEFFY?si=xEf1HppyU_ExXYYY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>


## Step 1: Sign up for an Obico account {#step-1-sign-up-for-an-obico-account}

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
2. Open the mobile app. Click through the first time tour and then tap **“Let’s Go!”**.
3. Simply tap "**YES!**" on the "Hardware Required" screen.
4. Tap "**Sign Up/Sign In**" button to proceed to the sign up/sign in screen.
5. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account.

:::info
If you are connecting to a self-hosted Obico Server, press the wrench icon (**🔧**) on the top-left corner of the sign-up screen to change the server address.
:::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/mobile-app-signup.gif" /></div>

  </TabItem>
  <TabItem value="web">

1. Open the [Obico Server sign up page](https://app.obico.io/accounts/signup/) in a new browser tab.
2. Sign up with your email, Google or Facebook account. If you have already registered, click the "Sign In" button and sign in to your account.

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

1. Press "Link Printer" button on the welcome screen. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "Link New Printer".
2. Choose “BTT Pi 2” on the next screen.
3. Click "Next"
4. The app will start scanning for the Klipper printer connected to the same local network.
5. If a printer is found, simply click the "Link" button and the app will do the rest for you.

:::tip
  If, however, the app can't find your Klipper printer after 1 minute of scanning, you need to follow the **[Manual Setup Guide](#link-manually)** to link your printer using a one-time passcode.
:::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-mobile.gif" /></div>
1. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
  <TabItem value="web">

1. On the welcome page, click the "**Link Printer**" button. 
2. Click "Generic Klipper" on the page that asks you to select a platform
3. Click "Next"
4. The app will start scanning for your Klipper connected to the same local network.
5. If your Klipper printer is found, simply click the "**Link**" button and the app will do the rest for you.

:::tip
  If, however, the app can't find your Klipper printer after 1 minute of scanning, you need to follow the **[Manual Setup Guide](#link-manually)** to link your printer using a one-time passcode.
:::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-web.gif" /></div>
1. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
</Tabs>

## Step 4: Restart the BTT Pi. {#restart-pi}

Once the BTT Pi has booted up, you should be able to see your printer and the webcam stream in the Obico app.

## What's next? {#whats-next}

### Check out your printer feed! {#check-out-your-printer-feed}

Press "Go Check Out Printer Feed!" to see everything you care about your printer: the webcam feed, heater temperature, time remaining on the print job, and more! Remember, you can see your printer feed anywhere you go, as long as you have an internet connection on your phone!

### Test the magical failure detection! {#test-the-magical-failure-detection}

The Detective sounds too magical to be true? [See The Detective in action for yourself](/docs/user-guides/how-to-test-failure-detection).

### Change printer settings. {#change-printer-settings}

The default settings for your printer in The Spaghetti Detective are the ones that most users find the most reasonable. But feel free to tweak them to your liking:

- [Change notification settings](/docs/user-guides/notification-settings) (mobile app only). By default you receive push notifications when The Detective finds something fishy, and for the status of whatever your printer is printing. But you can choose to receive a lot more.
- [Change printer settings](/docs/user-guides/detection-print-job-settings), such as if The Detective should pause your printer when a failure is detected.

## Link Your Printer Manually With One-Time Passcode  - Mobile and Web{#link-manually}

:::tip
Only follow this section if linking your printer automatically in [step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app) did not work.
:::

### Link Your Printer Manually Using KlipperScreen {#link-your-printer-manually-using-klipperscreen}

If you have KlipperScreen installed using the firmware provided by BigTreeTech, you can link your printer to Obico by scanning a QR code on your KlipperScreen. 


1. From the main printer dashboard in KlipperScreen, tap **"More"**. 
2. Tap **"Obico"** Now you will see a screen with a QR Code.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/btt-pi-2-guide/btt-pi-2-link-obico-klipperscreen.gif" /></div>

3. Go back to the printer scanning screen in the mobile app (from [Step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app)), tap **"switch to manual linking".** 
4. Tap **"Touch Screen"** 
5. Click **"Allow"** to give permission to allow the Obico app to access your camera. 
6. Aim the camera at the QR code on your KlipperScreen to link your printer. 

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/btt-pi-2-guide/btt-pi-2-klipperscreen-qr-code.jpeg" /></div>

7. Go to **[step 4 of the setup guide](#restart-pi)** to  complete the installation.

### Link Your Printer Manually **Without** KlipperScreen {#link-your-printer-manually-without-klipperscreen}

If you are not using a screen or you are using the web app, you can get the one-time passcode to link your printer through SSH. 

1. Use a terminal to ssh to your BTT Pi 2  


**Username:** Biqu

**Password:** Biqu
   
2. Run the following commands

```cd moonraker-obico```

```./install.sh```

3. Follow the instructions given in the terminal

4. Go back to the printer scanning screen in the mobile app (from [Step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app)), tap **"switch to manual linking".** 
5. Tap **"KIAUH or ./install.sh"**
6. Enter the one-time passcode shown on the terminal screen into the Obico app.

5. Go to **[step 4 of the setup guide](#restart-pi)** to  complete the installation.






