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

:::tip
This guide is for users who installed Klipper themselves. If you have a printer that came with Klipper pre-installed, follow the guide for your 3D printer:
- [Creality K1 Series](https://www.obico.io/blog/remote-access-creality-k1/)
- [Elegoo Neptune 4 Series](/blog/elegoo-neptune-4-and-obico-ai-3d-printing-revolution/)
- [Kingroon KLP1](/blog/kingroon-klipper-remote-access-and-ai/)
- [Kingroon KP3S Pro V2](/blog/kingroon-klipper-remote-access-and-ai/)
- [Qidi X Series](/blog/qidi-tech-x-series-klipper-remote-access-and-ai/)
- [Creality Sonic Pad](https://www.obico.io/blog/sonic-pad-remote-access-ai/)
- [Sovol SV08 Series](/blog/sovol-svo7-series-klipper-remote-access-ai/)
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
7. Follow the guide outlined in Step 3 to either link your Klipper machine and Obico automatically or manually by using the one-time passcode.
    * You do not need the one-time passcode if automatic linking is successful below.

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

1. Press "Link Printer" button on the welcome screen. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "Link New Printer".
2. Choose **“Generic Klipper”** on the next screen.
3. Assuming you have followed the previous steps and installed the plugin, you can simply click the **"Yes, the Plugin is Installed"** button.
4. The app will start scanning for the Klipper printer connected to the same local network.
5. If a printer is found, simply click the **"Link"** button and the app will do the rest for you.
:::tip
  If, however, the app can't find your Klipper printer after 1 minute of scanning, you need to follow the **[Manual Setup Guide](#link-manually)** to link your printer using a one-time passcode.
:::

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-mobile.gif" /></div>
1. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
  <TabItem value="web">

1. On the welcome page, click the "**Link Printer**" button.
2. Click **"Generic Klipper"** on the page that asks you to select a platform
3. Assuming you have followed the previous steps and run the `install.sh` script, simply press **"Next"**.
4. The app will start scanning for your Klipper connected to the same local network.
5. If your Klipper printer is found, simply click the "**Link**" button and the app will do the rest for you.

:::tip
  If, however, the app can't find your Klipper printer after 1 minute of scanning, you need to follow the **[Manual Setup Guide](#link-manually)** to link your printer using a one-time passcode.
:::


<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/auto-link-klipper-web.gif" /></div>
1. Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

  </TabItem>
</Tabs>

## Step 4: Restart the Raspberry Pi. {#restart-pi}

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




## Link Your Printer Manually With One-Time Passcode {#link-manually}

:::tip
Only follow this section if linking your printer automatically in [step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app) did not work.
:::


If your printer is not recognized automatically, you can link your printer with a one-time passcode instead.

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

:::tip
  If you are on Obico for Klipper version older than 1.6.0, switch to **[Legacy Manual Setup Guide](https://obico.io/docs/user-guides/klipper-setup-manual-link)** to link your printer using a six-digit code.
:::

1. Click "Switch to Manual Linking" button on the printer scanning page.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/mobile-switch-to-manual-link-klipper.gif" /></div>


2.  Go back to the terminal window you had open in Step 2. Note the one-time passcode shown on the terminal screen

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/obico-klipper-one-time-passcode.png" /></div>


3. Type the one-time passcode into manual linking page of the Obico web app. You're printer will be securely linked to your Obico account.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/mobile-manual-link-to-klipper.gif" /></div>

4. Go to **[step 4 of the setup guide](#restart-pi)** to  complete the installation.


  </TabItem>
  <TabItem value="web">

:::tip
  If you are on Obico for Klipper version older than 1.6.0, switch to **[Legacy Manual Setup Guide](https://obico.io/docs/user-guides/klipper-setup-manual-link)** to link your printer using a six-digit code.
:::

1. Click **"Switch to Manual Linking"** button on the printer scanning page.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/switch-to-manual-linking.png" /></div>


2.  Go back to the terminal window you had open in Step 2. Copy the one-time passcode shown on the terminal screen

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/obico-klipper-one-time-passcode.png" /></div>

3. Paste the one-time passcode into manual linking page of the Obico web app. You're printer will be securely linked to your Obico account.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/manual-setup-one-time-passcode.gif" /></div>


4. Go to **[step 4 of the setup guide](#restart-pi)** to  complete the installation.




  </TabItem>
</Tabs>



