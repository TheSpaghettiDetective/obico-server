---
id: nozzle-camera-printer-installation
title: How to Install a Nozzle Camera on Your 3D Printer
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


:::warning
This guide is deprecated. We are no longer maintaining this guide. Please refer to our nozzle camera partners, Mintion and 3DO for nozzle camera installation guides and tutorials. You are still welcome to use an endoscope nozzle camera, but they are not officially supported, it is up to you to come up with a mounting solution for your 3D printer.
:::

This guide will walk you through how to install a nozzle camera on your 3D printer. We recommend the cameras:

- Any [USB endoscope camera](https://www.amazon.com/Seesi-Endoscope-Waterproof-Inspection-Semi-Rigid/dp/B07PBF6DX5/) with at least 720P. There are many printable mounts for a variety of USB endoscope cameras for many different 3D printers. Find a mount and endoscope combination that works for you or design your own mount for your USB endoscope of choice.
- Mintion Nozzle Camera
- The 4K Nozzle Camera from 3DO is an awesome high-quality camera designed specifically to be used as a nozzle camera. There are ready-made mounts for a variety of [3D printers](https://github.com/3DO-EU/nozzle-camera/tree/main/printers). If you are in the US or Canada, you can get a 3DO nozzle camera from [KB3D](https://kb-3d.com/store/electronics/779-3do-nozzle-camera-kit.html) or [Fabreeko](https://kb-3d.com/store/electronics/779-3do-nozzle-camera-kit.html). If you are in Europe, you can get it from [3DO](https://3do.eu/59-nozzle-camera) directly.

We have detailed guides for the Prusa Mini and the Voron StealthBurner as well as some recommendations for other printers. We will add additional detailed printer guides in the future.



<Tabs>
<TabItem value="Prusa-Mini" label="Prusa Mini" default>

:::note
This guide was initially created specifically for Prusa Mini 3D printers, but most of the instructions can be applied to most common 3D printers such as Creality Ender 3 and other similar printers. Installing the nozzle camera on another printer will require some connecting the dots, but it should be mostly straightforward if you use this guide.
:::


This guide has been adapted from and inspired by Ananord’s guide on [Instructables](https://www.instructables.com/3D-Printer-Layer-Cam-Nozzle-Cam-Prusa-Mini/) and Chilicoke’s Nozzle Camera [Youtube guide](https://www.youtube.com/watch?v=GAp23w_dnNc&t=10s) in addition to other work from the community.

This guide will show you how to install an endoscope camera on your Prusa Mini 3D printer. This setup will assume you already have your Prusa mini connected to OctoPrint running on a Raspberry Pi.


Required Components:

![](/img/blogs/prusa-mini-nozzle-camera-setup/001.jpeg)


1. 5.5mm USB-C Endoscope Camera from [Amazon](https://www.amazon.com/dp/B09NVYXTG5?psc=1&ref=ppx_yo2ov_dt_b_product_details) or similar

2. [Reinforced](https://www.printables.com/model/432351-prusa-mini-endoscope-nozzle-cam-mount) or [Standard 3D printed mount for Prusa Mini/Mini+ by Scorrigan87](https://www.printables.com/model/419131-nozzle-camera-with-less-movement-55mm-endoscope-mo) - (remix of the original mount by [Shadow703793](https://www.printables.com/social/41644-shadow703793))


3. M4 x 20 socket head cap screw (or similar) and M4 Nut

4. Permanent marker

:::note
Since writing this guide, the 3DO nozzle camera now has a compatible mount for [Prusa Mini 3D printers](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/Prusa%20Mini). If you prefer it, you can get a 3DO camera from [Fabreeko](https://www.fabreeko.com/products/nozzle-camera-by-3d0?variant=44184256446719) or [KB3D](https://kb-3d.com/store/electronics/779-3do-nozzle-camera-kit.html)
:::

## Prepare the mount {#prepare-the-mount}

![](/img/blogs/prusa-mini-nozzle-camera-setup/002.jpeg)

1. **Print the endoscope mount found on Printables.com.**

a. The mount will not be anywhere near the hotend, so it can be printed in any material. In this case, we printed it with Polymaker PLA with 6 perimeters and 25% infill.

2. **Assemble the mount**

![](/img/blogs/prusa-mini-nozzle-camera-setup/003.jpeg)

a. This simple mount attaches to the rear 5015 fan on the Prusa Mini/Mini+ with a M4x20 Socket head cap screw and an M4 nut.

![](/img/blogs/prusa-mini-nozzle-camera-setup/004.jpeg)

   b. A M3x6 (or similar) screw can be used as a set screw to to keep the camera from twisting when the printer is moving. If you printed the mount vertically, keep in mind that this hole is not super strong, so you may consider pre-drilling the hole with an m3 drill bit if the fit is too tight.


![](/img/blogs/prusa-mini-nozzle-camera-setup/005.jpeg)

3. **Install the mount**

a. Install the mount on the fan using the M4x20 screw and M4 nut as shown. Do not connect the camera yet.

## Prepare the camera {#prepare-the-camera}

1. **Connect the camera to OctoPrint.**

![](/img/blogs/prusa-mini-nozzle-camera-setup/006.jpeg)

a. Connect the USB-C to USB adapter (included with the camera) and plug the camera into your Raspberry Pi running OctoPrint.
b. Connect to OctoPrint to ensure the camera is working properly. Restart OctoPrint if no image is shown.

2. **Determine the direction of the camera**

a. Since the camera is cylindrical, it is difficult to determine the direction without looking at the live camera feed. Determine the direction of the camera and use a sharpie to mark the up position of the camera. Do not worry about making it perfect, we will adjust the positioning in a later step.


## Mount the camera {#mount-the-camera}

1. **Insert the endoscope into the mount**

![](/img/blogs/prusa-mini-nozzle-camera-setup/007.png)

a. Place the endoscope so that the camera nozzle is correctly oriented in OctoPrint’s webcam stream.

![](/img/blogs/prusa-mini-nozzle-camera-setup/008.png)

![](/img/blogs/prusa-mini-nozzle-camera-setup/009.jpeg)

 b. The camera used in this guide has a focal length of 30-100mm, but testing has shown that positioning the camera between 30-50mm from the nozzle, angled slightly down, works best.


2. **Cable Management**

a. Before tightening the set screw to position the camera into its final place, use zip ties to route the cables along the cable loom that is already in place, Be sure to use a zip tie as close to the bottom of the cable loom as possible to fix the point of the cable and prevent movement while the printer is in motion. This step can be tricky with the rigid cables used with these endoscopes, but try your best to get the cable routed and secured firmly. Test your work by moving the toolhead slowly side to side and up and down to simulate printing.

3. **Tighten the set screw**

a. Ensure the position of the camera is as desired and then tighten the set screw to secure the camera.

:::note
If the camera still isn’t secure, you can wrap a small piece of masking or electrical tape around the base of the camera to increase its’ diameter slightly to create a tighter fit.
:::


## Set higher camera resolution {#set-higher-camera-resolution}

:::tip
The information below assumes you will add the endoscope camera in replacement of any other camera you have installed. If you are comfortable, you may prefer to set up the endoscope camera as a second camera. You can follow Charlie Powell's [guide to add the endoscope as a second camera](https://community.octoprint.org/t/setting-up-multiple-webcams-in-octopi-the-right-way/32669). Just be sure to set the endoscope camera resolution to 1280x720.
:::

Unless you have otherwise changed it, your camera stream defaults to a resolution of 640x480 at ten frames per second. For data collection, we want to capture images at a slightly higher resolution.

1. **SSH to your Raspberry Pi**
   a. Ssh to your Raspberry Pi running OctoPrint and enter the following command:

`sudo nano /boot/octopi.txt`

   This will open the nano text editor inside the terminal. Using the arrow keys on your keyboard to navigate the cursor, change the camera from auto to usb by editing this line:

`#camera="auto"`

   To become:

`camera="usb"`

2. **Change the resolution**
   a. Change the resolution from 640x480 to 1280x720 by changing the following line from:

`#camera\_usb\_options="-r 640x480 -f 10"`

   To:

`camera\_usb\_options="-r 1280x720 -f 10"`

   Enter "Control-O" on your keyboard to write the file and "enter" to confirm the file name.

1. **Restart webcamd**

a. Restart the webcamd by entering the following command:

`sudo service webcamd restart`




:::note
Due to Raspberry Pi CPU performance, there is a necessary tradeoff between resolution and framerate. During testing, we have been able to run the endoscope camera at 1280x720 resolution at 10 frames per second, but we have occasionally seen the CPU get overloaded when running this way. If you get a CPU usage warning, try changing the resolution to 960x720 or lowering the frame rate to 5 frames per second
:::

</TabItem>
<TabItem value="StealthBurner" label="Voron StealthBurner">

This guide will walk you through installing the 3DO 4K nozzle camera on your Voron 2.4 3D printer with a StealthBurner tool head.


## Required Hardware: {#required-hardware}

![](/img/blogs/nozzle-camera-stealthburner/001.png)

1. Voron 2.4 with StealthBurner
2. 3DO 4K nozzle camera kit (distributed by [3DO](https://3do.eu/nozzle-camera/763-1162-3do-nozzle-camera.html) for EU and [KB3D](https://kb-3d.com/store/electronics/779-7659-pre-order-3do-nozzle-camera-kit-multiple-styles.html#/914-resolution-4k) or [Fabreeko](https://www.fabreeko.com/products/nozzle-camera-by-3d0?variant=43751816593663) for U.S.)
- The kit includes
  - 4K Camera
  - 2\*10mm SHCS screws (for PCB mounting) -4x
  - [5050 SK6812 WWCW 6000K LED](https://3do.eu/nozzle-camera/804-3do-5050-wwcw-sk6812-led-2pcs.html) - 2x
  - [1x High-quality high-temperature USB cable (FEP + Silicone)](https://kb-3d.com/store/wiring-connectors/780-7660-pre-order-3do-usb-cable-for-nozzle-camera-usb-a-to-5p-multiple-styles.html#/915-length-07_meters)


## Printed Parts {#printed-parts}

You will need to print a new main body for the stealth burner to accommodate the nozzle camera. Head over to the [nozzle camera github page](https://github.com/3DO-EU/nozzle-camera) and find the main body for your hotend.

In the StealthBurner section of the repository, you will find sets of files for standard StealthBurner hotends and extended StealthBurner hotends such as the Phaetus Rapido or the Slice Engineering Mosquito Magnum Plus.


For example, print the following parts for standard stealth burner hotends:

- [Cam_mount](https://github.com/3DO-EU/nozzle-camera/blob/main/printers/Voron_StealthBurner/Cam_mount_SB.stl) (stealth burner main body) - 1x
- [Pcb_mount](https://github.com/3DO-EU/nozzle-camera/blob/main/printers/Voron_StealthBurner/PCB_mount_SB.stl) (stealth burner adxl345 mount) - 1x



## Install the camera {#install-the-camera}

![](/img/blogs/nozzle-camera-stealthburner/002.png)

Photo Courtesy of [3DO Github](https://github.com/3DO-EU/nozzle-camera)


Install the camera as shown above. The ribbon cable is somewhat delicate but it can be folded to help route it. Be careful not to fold it back and forth multiple times to avoid damaging it.

![](/img/blogs/nozzle-camera-stealthburner/003.png)

Photo Courtesy of [3DO Github](https://github.com/3DO-EU/nozzle-camera)


The PCB can be mounted to the fan with VHB tape (only tested with LGX lite extruder) or it can be mounted on the outside using the four included screws and the pcb\_mount which is the same as the ADXL345 mount for the StealthBurner.



## Lights {#lights}
:::tip
The led lights included in the [KB3D kit](https://kb-3d.com/store/electronics/779-pre-order-3do-nozzle-camera-kit.html) and [Fabreeko kit](https://www.fabreeko.com/products/nozzle-camera-by-3d0?variant=43751816593663) are quite a bit brighter than the ones specified in the [StealthBurner BOM](https://vorondesign.com/voron_stealthburner), so you may want to consider swapping the lights.
:::

If you plan to use the nozzle camera long term, you may find it easiest to re-use the components such as lights, fans, etc from your StealthBurner main body already installed on your printer. If you plan to do this, simply swap the components from the old part to the new one.

If you plan to install new components (lights and fans) on the main body, head over to the [Voron StealthBurner manual](https://github.com/VoronDesign/Voron-StealthBurner/raw/main/Manual/Assembly_Manual_SB.pdf) after installing the camera and follow the instructions as you did previously.

## Set camera resolution to 4096x3840 {#set-camera-resolution-to-4096x3840}

1. Open your preferred web interface such as Mainsail or Fluidd.
2. Go to *Machine*. Open the folder that contains your webcam settings such as `crowsnest.conf`

![](/img/blogs/nozzle-camera-stealthburner/set-resolution.png)

3. Edit the resolution for the nozzle camera to be 4096x3840 or the maximum resolution that your webcam can handle

:::warning
This is a very high resolution. It may not produce a good quality webcam stream in Mainsail/Fluidd or Obico. You can change back to a normal resolution when not running Celestrius tests.
:::

If you get warnings about Obico consuming too much CPU power, you can [disable the webcam in Obico](https://www.obico.io/docs/user-guides/moonraker-obico/config/) by setting `disable_webcam_streaming = True` under `[webcam]` in the moonraker-obico.cfg file.

## Data collection {#data-collection}

Once your stealth burner is fully assembled and installed, you are ready for data collection.  You can now move onto collecting the data. You will need to install a special plugin for data collection. Follow the [First Layer AI Data Collection (Project Celestrius)](https://app.obico.io/ent/celestrius_alpha_enroll/) to get started.



## FAQ (Adapted from 3DO) {#faq-adapted-from-3do}

- **Does it work in an enclosed printer?**

Yes, though our camera is rated at 60C we have been running it for 48hrs in a 70C industrial heat chamber without any issues.

- **Why is FPC so long?**

We decided on having 25cm between the camera and PCB for more flexibility on future mount designs.

- **Can I bend/fold the FPC to make it shorter?**

Yes, FPC is flexible and can be bent, if you want to fold it (180deg) we recommend doing this max one time in the same spot, or else you risk breaking the lanes inside FPC.

Example of folding FPC

![](/img/blogs/nozzle-camera-stealthburner/006.jpeg)

- **What are the camera specifications?**


|<p><h2></h2></p><p><h2>**4K (Sony IMX258)**</h2></p>|<h2></h2>|
| :- | :- |
|<h2>**Sensor Size**</h2>|<h2>1/3.06</h2>|
|<h2>**Mega-Pixel**</h2>|<h2>13MP</h2>|
|<h2>**Frame Rate**</h2>|<h2>30FPS@4K 60FPS@1080P</h2>|
|<h2>**Lens type\***</h2>|<h2>Fixed Focus</h2>|
|<h2>**FoV**</h2>|<h2>80Deg</h2>|
|<h2>**Operating temperature\*\***</h2>|<h2>-20°C TO 60°C</h2>|
|<h2>**Storage temperature**</h2>|<h2>-40°C TO 80°C</h2>|

*Focus distance from the back side of the camera to the object is set to 34.5mm

(It’s possible to change the focus distance by breaking glue seal holding the lens in place and rotating the lens. Be sure to re-apply glue after adjustment)

**Tested in a 70C heat chamber for 24hrs without any issues. Not recommended for machines with high chamber temperatures.



Obico has no affiliation with the Nozzle Camera from 3DO, but they are a great team making an awesome nozzle camera product!

## Thanks to the contributors that made the 3DO Nozzle Camera project possible {#thanks-to-the-contributors-that-made-the-3do-nozzle-camera-project-possible}

CAD Design & Testing

- Olof Ogland (Known from Bondtech)
- Kenneth Munkholt (VZ Community)
- Dennis Jespersen (From RatRig Community)

Software Development & Testing

- Meteyou (Mainsail founder)
- KwadFan (Crowsnest founder)
- Rogerlz(Crowsnest Tester)

Beta Testers

- Mitsuma (From RatRig Community)
- Joao Barros (From RatRig Community)

</TabItem>

<TabItem value="Other-Printers" label="Other Printers and Compatible Mounts" default>

Nozzle camera options for other specific printers

While we have specific guides for Prusa Mini and Voron printers, there are many working nozzle camera mounts and guides out there. Below, we will list some that we have come across. Although there is not a detailed guide for these mounts, installation is similar to installation on the Prusa mini or Voron, but of course there will be some specific differences based on your 3D printer.

The [3DO nozzle camera](https://3do.eu/59-nozzle-camera) currently has ready to print mounts for the following 3D printers.

- [EVA 2.4](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/EVA_2_4)
- [Eva 3](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/EVA_3)
- [Prusa i3 MK3](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/Prusa%20I3%20MK3)
- [Prusa Mini](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/Prusa%20Mini)
- [Voron StealthBurner](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/Voron_StealthBurner)
- [VzBot](https://github.com/3DO-EU/nozzle-camera/tree/main/printers/VzBoT)


Endoscope cameras are much lower quality than the 3DO nozzle camera, but they will still work for the purpose. We have experimented with a number of Endoscope cameras. As long as it is at least 720P, it should be fine.  Here are some various Endoscope camera mounts available thanks to the community. In most cases, a specific endoscope is recommended on the model page.

- [Nozzle Camera for Ender 3/Cr-10](https://www.printables.com/model/354575-nozzle-camera-for-ender-3-cr-10) by [Nik Sajevik](https://www.printables.com/@NikSajevic_422397) on Printables
- [Endoscope Mount for Anycubic i3 Mega](https://www.thingiverse.com/thing:4779427) by [macsims](https://www.thingiverse.com/macsims) on Thingiverse
- [Ender 3V2 5.5mm Endoscope mount for Ender 3V2](https://www.printables.com/model/500359-ender-3-v2-55mm-endoscope-mount) by [Tim Williams](https://www.printables.com/@TimWilliams_342484) on Printables.
- [Endoscope Mount for Ender 3, CR-10](https://www.printables.com/model/16299-endoscope-mount-for-ender-3-cr-10) by [Makers Mashup](https://www.printables.com/@MakersMashup_42322) on Printables

If you find another endoscope mount that works for you, or you make one yourself, please let us know! We would love to include it on our list!
</TabItem>
</Tabs>
