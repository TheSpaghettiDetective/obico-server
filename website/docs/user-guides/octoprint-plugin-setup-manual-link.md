---
id: octoprint-plugin-setup-manual-link
title: Manually Link OctoPrint with a 6-digit code
sidebar_label: Manually Link OctoPrint
---

Follow this guide in one of these 2 rare cases:

* You are trying to re-link OctoPrint. There are only [a few reasons](/docs/user-guides/relink-printer/) why you need to re-link OctoPrint.
* Your OctoPrint can't be identified at the last step in [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup/). You don't need a 6-digit code if your OctoPrint can be identified and linked automatically.

:::caution
If you are setting up Obico for the first time, you should follow [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup) first. **Please DO NOT PROCEED** if you haven't done so.
:::


:::info
This guide assumes you are connecting to the [Obico Cloud](https://app.obico.io). If you are connecting to a [self-hosted Obico Server](/docs/server-guides/), you will need to use the address of your self-hosted server.
:::


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Step 1: Launch the Setup Wizard in the plugin {#step-1-launch-the-setup-wizard-in-the-plugin}

:::note

Most of the time the Setup Wizard will automatically launch when you open OctoPrint. Skip this step if it's the case.

:::

1. Open OctoPrint page in a browser.
1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down to the bottom of the list on the left-hand side.
1. Click "**Obico for OctoPrint**".
1. Click "**Troubleshooting**".
1. Scroll down to the bottom, and click "**Re-run Wizard**".

![Install the Plugin](/img/user-guides/setupguide/tsd-plugin-rerun-wizard.gif)

## Step 2: Follow the Setup Wizard {#step-2-follow-the-setup-wizard}

:::note

Follow instructions in the "**📱  Mobile App**" tab if you are using The Spaghetti Detective mobile app, or the "**🌐  Web App**" tab if you are using the web app.

:::

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Click the "**Setup Plugin**" button.
1. On the next page, click on “**Continue with Mobile App**".
1. Since you have already downloaded the mobile app and signed up for an account, just click “**Continue**” here.
  :::caution
  If you haven't signed up for an Obico account, stop here and follow [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup) first.
  :::
1. Now you should see a page that asks you for a 6-digit verification code. Keep this browser tab open while you obtain the 6-digit code in The Spaghetti Detective app.

![Obico Wizard Page](/img/user-guides/setupguide/octoprint-plugin-verification-code.png)

  </TabItem>
  <TabItem value="web">

1. Click the "**Setup Plugin**" button.
1. On the next page, click on “**Continue with Web Site**".
1. Since you have already signed up for an account, just click “**Continue**” here.
  :::caution
  If you haven't signed up for an Obico account, stop here and follow [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup) first.
  :::
1. Now you should see a page that asks you for a 6-digit verification code.

![Obico Wizard Page](/img/user-guides/setupguide/octoprint-plugin-verification-code.png)

  </TabItem>
</Tabs>

## Step 3: Launch the "Link Printer" wizard in the Obico app {#step-3-launch-the-link-printer-wizard-in-the-obico-app}

:::note
If you wan to re-link OctoPrint to an existing printer, you should do [step 3a](#step-3a-launch-the-re-link-printer-wizard-in-the-obico-app) instead.
:::

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

Open the Obico mobile app. You should see a screen with a big "**Link OctoPrint**" button. If you don't see that screen, tap the menu icon (☰) on the top-left corner, and select "Link New Printer".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/launch-manual-link-mobile.jpg" /></div>

  </TabItem>
  <TabItem value="web">

Open the [Obico web app](https://app.obico.io/) in another browser tab. You should see a screen with a big "**Link Printer**" button.  Click that button.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/launch-manual-link-web.jpg" /></div>

  </TabItem>
</Tabs>

## Step 3a: Launch the "Re-Link Printer" wizard in the Obico app {#step-3a-launch-the-re-link-printer-wizard-in-the-obico-app}

:::note
If you want to link OctoPrint to a new printer, you should do [step 3](#step-3-launch-the-link-printer-wizard-in-the-obico-app) instead.
:::

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. From the printer screen, click the kebab menu (⋮) on the top right of the screen.
2. Click "**🔧 Advanced Settings**".
3. Scroll down to the bottom and click "**Re-link Printer**".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/launch-relink-wizard-mobile.gif" /></div>

  </TabItem>
  <TabItem value="web">
1. From the printer screen, click the kebab menu (⋮) on the top right of the screen.
2. Click "**🔧 Configure**".
3. Scroll down to the bottom and click "**Re-link Printer**".

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/launch-relink-wizard-web.gif" /></div>

  </TabItem>
</Tabs>


## Step 4: Obtain the 6-digit code in The Spaghetti Detective app {#step-4-obtain-the-6-digit-code-in-the-spaghetti-detective-app}

<Tabs
  groupId="app"
  defaultValue="mobile"
  values={[
    {label: '📱  Mobile App', value: 'mobile'},
    {label: '🌐  Web App', value: 'web'},
  ]}>
  <TabItem value="mobile">

1. Choose "**OctoPrint**" on the next screen.
1. Assuming you have followed [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup/) and installed the plugin, you can simply click the "**Yes, plugin is installed**" button.
1. Now you will see a screen with a 6-digit verification code. This is the code you will use to link your printer. You can long-press the number to copy it to the clipboard.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/klipper-verification-code-mobile.jpg" /></div>

  </TabItem>

  <TabItem value="web">

1. Assuming you have followed [Obico for OctoPrint setup guide](/docs/user-guides/octoprint-plugin-setup/) and installed the plugin, you can simply click the "**Next>**" button.
1. On the next screen, if it is stuck in "Scanning..." for more than 1 minutes, tap the "**Manual Setup**" link.
1. Tap "**Next >**" on the next screen.
1. Now you will see a screen with a 6-digit verification code. This is the code you will use the manually link OctoPrint. You can press Ctrl-C (Windows) or Cmd-C (Mac) to copy the 6 digit code to the clipboard.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/manual-link-web.gif" /></div>

  </TabItem>
</Tabs>

## Step 5: Enter the 6-digit code in the plugin Setup Wizard {#step-5-enter-the-6-digit-code-in-the-plugin-setup-wizard}

1. Go back to the browser tab in which your OctoPrint is open.
1. Enter the 6-digit code you obtained in [the previous step](#step-3-link-octoprint-to-your-the-spaghetti-detective-account). You can press Ctrl-V (Windows) or Cmd-V (Mac) to paste the code if you have previously copied them in the clipboard.
1. Restart OctoPrint. This is necessary only if you are re-linking OctoPrint.

<div style={{display: "flex", justifyContent: "center"}}><img src="/img/user-guides/setupguide/tsd-plugin-code-success.gif" /></div>
<br />

**Hooray! You are done! You can close the Setup Wizard window now.**

## Step 6 (optional): Give your printer a shiny name! {#step-6-optional-give-your-printer-a-shiny-name}

Optionally, you can now give your printer a name. If you skip this step, your printer will have the default name "*My Awesome Cloud Printer*".

<b />

