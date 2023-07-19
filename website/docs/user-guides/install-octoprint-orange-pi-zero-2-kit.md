---
title: Orange Pi Zero 2 Kit for OctoPrint Setup and Configuration
toc_min_heading_level: 2
toc_max_heading_level: 5
---

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/kit.png)

import TOCInline from '@theme/TOCInline';

<TOCInline toc={toc} />

This guide is intended for users with a varied range of technical experience. If you are a wiz, feel free to disregard the detailed explanations. If you have little experience, follow the instructions and you'll have OctoPrint connected to your 3D printer with a webcam in no time.

## **What's Included in the Kit** {#whats-included-in-the-kit}

- Orange Pi Zero 2
- Heat Sink with thermal pad
- USB Hub
- Case (not recommended - use the printable version)

:::caution
If possible, do NOT use the stock case included in the kit. The stock case doesn't having sufficient cooling and may cause the CPU to overheat.

Use the printable version instead.
:::

**You will also need**

- A high quality SD card (class 10 or better) with at least 8GB of storage
- An Ethernet cable
- USB cable to connect your 3D printer to the Orange Pi (comes with most printers)

## **Prepare the Software** {#prepare-the-software}

### **1. Download the OctoPrint for Orange Pi software** {#1-download-the-octoprint-for-orange-pi-software}

Download the OctoPrint for Orange Pi software [here](https://www.obico.io/download/orangepi_zero2_images/Orangepizero2_3.0.6_debian_bullseye_OctoPrint_1.8.6-20221201.img.zip)

- (Mac) Double click the file once downloaded and drag it into the applications folder to install it. (Windows users can right click the file and click extract to unzip the file)

### **2. Download Raspberry Pi Imager** {#2-download-raspberry-pi-imager}

- Go to [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
- Download the Raspberry Pi Imager software (available for Windows and Mac)
- Unzip the file

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/raspberry-pi-imager.png)

### **3. Flash the SD card** {#3-flash-the-sd-card}

- Open up the Raspberry Pi Imager

- Click _Choose Operating System_

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/choose-custom.png)

- Select Use Custom at the bottom of the menu

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-debian-image.png)

- Locate the file that you previously downloaded and unzipped and select it.

- Insert your SD card into the computer.

:::tip
Use a high-quality, class 10 or better SD card with at least 8GB of storage. If you plan on creating a lot of time-lapses, more storage is recommended.
:::

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/select-sd-card.png)

- Select the SD card

:::note
The SD card will be wiped, so be sure there are no important files on the card.
:::

- Click Write:

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/rpi-imager-warning.png)

- Confirm that you are aware the SD card will be erased. You may be asked to enter your administrator password for your computer as well.

:::tip
The file is large, so it may take a while (up to 40 minutes but likely less) for the software to be installed on the SD card. Grab a coffee, and get the rest of the kit setup while the software is installed on the SD card.
:::

## **Setup the Hardware** {#setup-the-hardware}

### **1. Unbox the Kit** {#1-unbox-the-kit}

Unbox your kit and lay out the components:

**The kit includes**

- Orange Pi Zero 2
- Heatsink
- USB Hub
- 5V 3A USB C Power Supply
- USB Webcam
- Official Orange Pi Zero 2 case (not recommended - use the printable version)

**You will also need**

- A high-quality SD card (class 10 or better) with at least 8GB of storage
- An Ethernet cable
- A USB cable to connect the Orange Pi to your printer (comes with most printers)

### **2. Install the heat sink on the Orange Pi Zero 2** {#2-install-the-heat-sink-on-the-orange-pi-zero-2}

- Remove one side of the paper backing on the thermal pad and place the pad on the heat sink. Remove the other paper from the other side and place the heat sink on the CPU

### **3. Put the Orange Pi in the Case** {#3-put-the-orange-pi-in-the-case}

While putting your Orange Pi Zero 2 is not required, it is recommended to help keep it clean and safe.

As mentioned above, it is not recommended to use the case that is included in the kit due to it's pour cooling capabilities. You can [print the case we designed](https://www.printables.com/model/322614-orange-pi-zero-2-case).

If you prefer a different case, we also made a [collection on Printables](https://www.printables.com/social/288649-obico/collections/346815) with a few other options that have been tested.

### **4. Mounting the Camera** {#4-mounting-the-camera}

You can mount your camera in many different ways depending on your printer. The best mounting solution depends on how you plan to use the camera with your 3D printer.

For example, If you are simply interested in casually monitoring your 3D prints with a camera, you don't have to consider any extra factors. Simply position your camera any way you like. If you are planning to use your webcam to record timelapse videos or take advantage of Obico's Ai failure detection, you may want to consider the angle of the camera further, it's focus and the lighting conditions. Here are a couple of options for mounting your camera:

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-camera-mount-1.jpg)

- Print a mount: 3D printing a mount is a great option. Here are a few mounts tested to work with the camera included with the kit.

| Webcam Mount                                                                                              | Description                                                                                                                                          |
| --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Tripod adapter for all webcams](https://www.printables.com/model/322584-usb-webcam-tripod-mount-adapter) | General tripod-mount (¼-20 thread)                                                                                                                   |
| [20-20 Extrusion Webcam Mount](https://www.thingiverse.com/thing:3147899)                                 | Works with printed [adapter](https://www.printables.com/model/322584-usb-webcam-tripod-mount-adapter)                                                |
| [Ender 3 S1 Mount](https://www.thingiverse.com/thing:5476426)                                             | Works with printed [adapter](https://www.printables.com/model/322584-usb-webcam-tripod-mount-adapter)                                                |

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-camera-mount-2.jpg)

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-camera-mount-3.png)

- Use a box, cup, or another surface to elevate the camera. Even a box can provide a nice camera view.

## **Configure Wifi** {#configure-wifi}

Once the Raspberry Pi Imager has finished flashing the OctoPrint software to your SD card, you can remove it from your computer and insert it into the Orange Pi.

### **1. Connect the Orange Pi to your router.** {#1-connect-the-orange-pi-to-your-router}

We will assume most users will be connecting via Wifi although connection via ethernet is recommended whenever possible.

- Connect one end of an ethernet cable to the Orange Pi, and connect the other end to a port on your wireless router. Assuming you will connect to wifi, this is only temporary, so do not worry if this is not where you plan to keep the device.
- Connect the included power supply to the Orange Pi and plug it into an electrical outlet.

### **2. Find the Pi's Ip Address** {#2-find-the-pis-ip-address}

- Now, you will need to find the IP address of your Orange Pi. This can be done in multiple ways. The easiest way is to connect to your router's admin portal.

:::tip
If you have an internet provider such as Verizon or Xfinity, instructions for connecting are on the router. In this example, I will access the Verizon wireless router settings by entering the admin username and password found on my router at mynetworksettings.com. The admin username and passwords are often different from the wifi username and password.
:::

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/wifi-router-1.png)

- Under Devices, find the device named orangepizero2. For Verizon routers, the IP address can be found by clicking the gear icon for a particular device.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/ip-address-router.png)

- You are looking for the IPv4 Address. Once you have found it, write it down or copy and paste it into your notes for easy reference.

If you are having trouble finding the IP address for your Orange Pi, there are a few other ways to find it.

- For Windows users, download Angry IP Scanner, a free software, and use it to scan for IP addresses. You are looking for the one that says _orangepizero2_

- Mac users can follow a similar process by downloading Lan Scan, a free IP scanner for mac.

:::tip
If you are not planning to configure wifi, you can skip the rest of this section and go to the **Connecting to OctoPrint** section.
:::

### **3. SSH into Your Orange Pi** {#3-ssh-into-your-orange-pi}

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/ssh-orange-pi.png)

- Now, open a terminal window. For Mac users, Terminal can be found in your applications Windows users will find the Command Prompt in programs.

- SSH into your Orange Pi. SSH is a secure way to access network services securely over an unsecured network. Type the following command:

```
ssh pi@your-ip-address
```

- Enter the password. The password is **orangepi.** You will not see the letters as you type the password, but they are still being entered.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/orange-pi-zero-2-welcome.png)

- Hit enter to confirm the password. You will then be greeted with the _Opi Zero2_ logo confirming you are logged in.

### **4. Connect to your wireless network** {#4-connect-to-your-wireless-network}

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/nmtui-connect-wifi.png)

- Enter the following command to open up the network configuration menu. You can simply copy and paste the command into the terminal and then hit enter on your keyboard to execute the command.

```
nmtui
```

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/edit-connection-nmtui.png)

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/activate-connection-nmtui.png)

- Use the arrow keys on your keyboard to highlight _Activate a connection_ and then use the cursor to highlight _OK_ and click enter.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/activate-wifi.png)

- Use the arrow keys again to highlight your wifi address name, and then hit enter on your keyboard.
- Enter the password for your wifi as it appears on your router. Hit enter to confirm.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/wifi-activated.png)

- You can verify your wifi has been connected successfully when the upper right indicator switches from \<activate\> to \<deactivate\>. Once confirmed, move the arrow key to back and hit enter.

### **5. Find your Wireless IP address** {#5-find-your-wireless-ip-address}

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/find-wlan.png)

- Next, lets get the wireless ip address that was assigned to your orangepi. Enter the following command and hit enter.

```
sudo ifconfig -a
```

- In the output, find the line that starts with _wlan0:_ and note the IP address next to _inet._ Write it down or store it in your notes for easy reference.

## **Connect the Orange Pi to your printer** {#connect-the-orange-pi-to-your-printer}

### **1. Move the Pi to it's permanent location** {#1-move-the-pi-to-its-permanent-location}

- Disconnect the Orange Pi from the ethernet cable, and move it to where you plan to connect it with your printer.

### **2. Connect the Hardware** {#2-connect-the-hardware}

- Plug USB hub cable into the orange pi.
- Plug the camera into the USB hub
- Plug the Printer cable into the USB hub.
- Plug the power cable into the Orange Pi and into the electrical outlet
- Plug the USB printer cable into the printer with the printer on.

## **Connect to OctoPrint** {#connect-to-octoprint}

### **1. Access the OctoPrint User Interface** {#1-access-the-octoprint-user-interface}

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-setup-wizard-1.png)

- Open an internet browser and enter the IP address you just found into the URL bar. You will be greeted with the OctoPrint Setup Wizard.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-access-control.png)

### **2. Complete the Setup Wizard** {#2-complete-the-setup-wizard}

- Follow the instructions on the screen to complete the setup wizard such as creating an account.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-printer-profile.png)

- Under _Defauilt Printer Profile_, enter the origin location (usually lower left), whether or not it has a heated bed, and the size of your printers build volume. These settings won't affect your prints, but they help enhance the overall user experience.

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/octoprint-webcam-view.png)

- Click _Finish_, and you will be sent to the OctoPrint User interface.
- Click _Connect_ on the left to connect your 3D printer to your Orange Pi Zero 2.
- Click _Control_ on the upper tab to see your webcam view.

That's it! You have successfully connected to OctoPrint!

## **Configure Obico for OctoPrint** - optional but encouraged :) {#configure-obico-for-octoprint---optional-but-encouraged}

Obico for OctoPrint extends OctoPrint's capabilities:

- Monitor and control your 3D printer from anywhere on any device - Use the Obico mobile app on the go, or access the full OctoPrint interface from anywhere with Obico's Tunneling feature.
- Get added peace of mind with Ai failure detection. Obico watches your prints for you and can alert you through your favorite notification service when a failure is detected. Fully configurable to get notified or pause the print when a failure is detected.
- Start, stop pause and cancel prints on the go from anywhere.
- Check in on your prints on the go with high quality webcam streaming

![](/img/user-guides/octoprint-orange-pi-zero-2-kit/obico-plugin-wizard-1.png)

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

## Step 1: Access "Obico for OctoPrint" plugin wizard. {#step-1-access-obico-for-octoprint-plugin-wizard}

1. Restart OctoPrint by clicking the **power button**
1. Click **Restart OctoPrint**. Wait for OctoPrint to reload.
   1.The Obico plugin setup wizard should popup once OctoPrint reloads. If it doesn't open automatically, open up the OctoPrint settings menu by clicking the **gear** icon. Then find **Obico for OctoPrint** in the menu, and click **run setup wizard**

![Install the Plugin](/img/user-guides/setupguide/install-plugin.png)

## Step 2: Sign up for an Obico account. {#step-2-sign-up-for-an-obico-account}

:::tip

Follow instructions in the "**📱 Mobile App**" tab if you are using the Obico mobile app, or the "**🌐 Web App**" tab if you are using the web app.

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
{label: '📱 Mobile App', value: 'mobile'},
{label: '🌐 Web App', value: 'web'},
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
{label: '📱 Mobile App', value: 'mobile'},
{label: '🌐 Web App', value: 'web'},
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
