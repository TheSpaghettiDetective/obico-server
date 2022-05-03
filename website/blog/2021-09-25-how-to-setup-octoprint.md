---
title: How To Setup OctoPrint the Easy Way
author: Neil Hailey
author_url: https://www.linkedin.com/in/neilhailey
author_image_url: "https://cdn-images-1.medium.com/fit/c/300/300/1*L2wRkwCzzk4_YQ6WplroVg.png"
tags: ['Tech', '3D Printer Remote Access', 'OctoPrint', 'How-to']
---


## What is OctoPrint and why do I need it?

![OctoPrint User Interface](/img/blogs/Octoprint-user-interface.PNG)

OctoPrint is the most popular 3D printing software for wirelessly monitoring and controlling your 3D printer. 

Hundreds of thousands of printers rely on OctoPrint's awesome snappy web interface daily to manage their workflows.   In addition there are a ton of awesome plugins that take the power of remote 3D printer monitor and control to a whole new level. In this guide, we will tell you what you need to get OctoPrint set up with your 3D printer and how install it. 

Prefer to watch a video to guide you through the process? Check out Thomas Sanladerer's tutorial!

<div className="videoWrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/HBd0olxI-No" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
</div>


<!--truncate-->

## Hardware

### What hardware do I need?

![OctoPrint Hardware Required](/img/blogs/octoprint-hardware.png)

Minimally, the following hardware is required:

-   Raspberry Pi
    - A [Raspberry Pi Model 3B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) or [Raspberry Pi Model 4B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) will work best. We recommend the 4B as it is more powerful and not much more expensive than the 3B.

-   USB power cord

-   USB printer cord

-   SD card (at least 16GB)

We also suggest the following items:

-   A case for the Raspberry Pi

-   Heat sinks

-   Ethernet cable if you are connecting to a router


### Where do I get the hardware?


There are two ways to acquire the hardware:
1. Buy the components separately: If you are interested in getting each component separately, Amazon is a great place to start, but there are also some great and highly reputable authorized Raspberry Pi dealers who have e-commerce sites. [Vilros](https://vilros.com/) and [The Pi Shop](https://www.pishop.us/) are two certified resellers but there are others as well. 

2. Kit: There are many kits that come with some or all of the hardware needed. [TH3D](https://www.th3dstudio.com/product/ezpi-pro/) sells an OctoPrint kit that includes everything you need to get started. You can find more complete kits on [octoprint.org](https://octoprint.org/merch/). [Canakit](https://www.canakit.com/raspberry-pi) is another popular brand that sells kits with most of the needed hardware included. Some of these kits come with OctoPrint already installed on the SD card while others simply provide the hardware needed.

### A camera is not required but you'll probaly want one
Adding a camera to OctoPrint allows you to watch the printer from another room or from another state with one of the awesome remote monitoring plugins like [The Spaghetti Detective](https://thespaghettidetective.com/). A camera will also enable you to record awesome time-lapse videos.

**Okay, but which camera should I get?**

There are hundreds if not thousands of cameras out there that will work for OctoPrint, it can be hard to pick. A Raspberry Pi camera or a USB webcam are the two main options to consider.

In our experience, Raspberry Pi cameras tend to provide better quality results, but they are not as easy to manage. You'll need to print a mount for it, and the ribbon cables can be quite a pain. 

The [Raspberry Pi Camera](https://www.pishop.us/product/raspberry-pi-camera-module/) or the [Raspberry Pi Camera V2](https://www.raspberrypi.org/products/camera-module-v2/) will give you pretty great results for monitoring your prints, but if you are interested in creating [high quality jaw-dropping time-lapse videos](https://www.youtube.com/watch?v=aubLuCFIejc), then you'll probably want to check out the [Raspberry Pi High Quality Camera.](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/)

## Setup and Install

### Download the Raspberry Pi Imager 

- Download the Raspberry Pi Imager from [raspberrypi.org/software](http://Raspberrypi.org/software)
- The software is available for both Windows and Mac.


### Install and run the imager

![Select Other Specific Purpose OS](/img/blogs/install-octopi-raspberry-pi-imager-specific-purpose-os.jpg)

-  Select _Choose OS,_ 
- Select _other specific purpose OS,_ 

![Select Octopi](/img/blogs/raspberry-pi-imager-select-octopi.png)

- Select Octopi. This will automatically download the latest version of the Octopi image from [octoprint.org](http://octoprint.org)

![Warning: SD card will be erased](/img/blogs/octopi-install-sd-card-wipe-warning.png)

-   Under _Choose Storage_, select the SD card that you want to install OctoPrint on. Make sure you don't have any important files on this SD card as it will be wiped.
- Don't click write yet You'll want to secure your Pi and configure the wifi first.

### Secure your Raspberry Pi

-   By default, the password to [SSH](https://en.wikipedia.org/wiki/Secure_Shell) into your Octopi instance is _raspberry_ and the username is _pi_. This is not very secure. You'll want to change the password to prevent possible attacks from malicious users.

![Enable SSH ](/img/blogs/raspberry-pi-imager-enable-ssh.jpg)

-   Press _Control+Shift+x_ (CMD+Shift+x on mac) to bring up the Raspberry Pi imagers advanced options menu.

-   Click enable SSH and enter a secure password for the raspberry pi user. The username is _pi_ and the password is the one you just created.

### Connect your Raspberry Pi to the internet

We recommend connecting your raspberry pi directly to your wireless router or home ethernet ports if possible as this will provide the best streaming results. However, most users do not have easy access to a wired connection, so we will assume you will want to configure wifi. 


### Configure Wifi with OctoPrint
![Configure Wifi ](/img/blogs/octopi-configure-wifi-raspberry-pi-imager.jpg)

-   With the Raspberry Pi imager, wifi configuration is a breeze. Simply enter your username and password under _Configure wifi._


-   Be careful, this entry is space and case sensitive, so enter the username and password exactly as it appears on your router.

-   Under the _country code_ section choose the country that you are in.

-   Click _save_ and then click _write._ Once complete, eject the SD card from your computer.


### Connect to OctoPrint

-   Put the SD Card into the bottom of the Raspberry Pi (upside-down).

-   Plug the power cable into the Raspberry Pi and the outlet. 

- It will take a moment for OctoPrint to connect. 
- **Tip**: Watch the green "ACT" led on the Pi. It will flash on and off for a while and then it will turn off. Once solid, your pi is connected to the internet and OctoPrint.

## Connect the Hardware

### Step 1: Connect the heatsinks
![Raspberry Pi Heatsinks ](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/Raspberry-Pi-Heatsink-Location.jpg)
If you have them, place the heat sinks on the Raspberry Pi.

### Step 2: Put the Raspberry Pi in the case

Place the Raspberry Pi into the case if you have one.  

![Snap Raspberry Pi into case](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/PutPiIncase.gif)


### Step 3: Plug the printer cable into the Pi.

Plug the printer cable (micro USB, mini USB, or standard printer cable depending on your 3D printer) into the Raspberry Pi.

![Plug-in micro USB Cable](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/PluginMicro.gif)

### Step 4: Plug the power cable into the Pi.

- Plug the USB C power adapter into the Raspberry Pi.

![Plug USB C into the Raspberry Pi](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/InsertUSBC.gif)

### Step 5: Connect the webcam

- If you are using a USB webcam, connect the webcam by plugging the usb cable into any of the USB ports on the Raspberry Pi.

![Connect the webcam](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/PlugInWebcam.gif)

- If you are using a Raspberry Pi camera, place the ribbon cable into the camera and the Pi as shown below. Be very careful with the cable.

![Ribbon cable in Raspberry Pi HQ Camera. Source: Raspberry Pi](https://www.musquetier.nl/downloads/RPi_Camera_cable_setup.jpg)

- Place the other side of the ribbon cable into the pi as shown below. The blue side of the cable should be facing the HDMI port on the Raspberry Pi.

![Raspberry Pi Ribbon Cable Source: Arducam](https://www.arducam.com/wp-content/uploads/2020/02/pi-4-to-cam-connection-2048x736.png)

## How Do I mount the camera?

![OctoPrint camera setup](/img/blogs/OctoPrint-In-A-Box-Setup-Guide/FullPrinterSetup.gif)

There are many different ways to mount your camera. 3D printed mounts, tripods, webcam arm mounts, or even old boxes will all work. 

Check out our article on [Ender 3 webcam setup for OctoPrint](https://www.thespaghettidetective.com/blog/2021/02/22/octoprint-ender-3-webcam-setup/) for a more details on webcam setup. While we demonstrate the setup on an Ender 3, the information will be relevant for most brands and models of 3D printers.

## Printer Connection

Turn your 3D printer on, if it isn't already.  

-   Plug the printer cable  into your 3D printer.
-   Plug the power cable into a power outlet.

**At this point, the Raspberry Pi should be powered on, connected to the internet and your 3D printer.**

## Access the OctoPrint user interface
To access the OctoPrint interface, open a web browser on your computer and type http://octopi.local into the url bar. This should bring you right to the OctoPrint login screen. 

**If octopi.local does not work, you will need to locate your Octopi's IP address.** 
You can locate your Octopi's IP address multiple ways. Here are two: 

- **Windows File Explorer**

- On a windows computer:
- Open the File Explorer
![Find Octopi IP Address](/img/blogs/octopi-local-not-working.PNG)
- Click the *Network* tab
- Note: If you have Network Sharing disabled, you will need to turn it on  in order to see your Pi in the network tab. 
- **Your home router** 
Another option is to find the IP address through your home Wi-Fi router settings. You will need your router username and password (this may be different from your WiFi password), and you will need to know your router's IP address. If you don't know it, PC Mag has a great article on [accessing your Wi-Fi Router's settings.](https://www.pcmag.com/how-to/how-to-access-your-wi-fi-routers-settings)

- Once you have your router's IP address and the username and password for the router, type the ip address into a browser url. It might be , "192.168.1.1" or it might be something else. 

- You will be greeted by some type of login screen. Enter your username and password. 

- You should see something like "connected devices." Select it, and you will see all of the devices currently connected to your router. The once with "Octopi" in it is the one you are looking for. Once you find it, type the IP address into a browser window. 


## Complete the Setup Wizard

![enter image description here](/img/blogs/octoprint-setup-wizard.jpg)

- Once you are able to access the OctoPrint Interface, follow the on-screen instructions to complete the Setup Wizard. 

- You'll want to set your 3D printer's build volume and nozzle diameter in the printer profile section. Note, this information does not change any slicer related Gcode settings, only controls within OctOprint. 

## Install Plugins

One of OctoPrints greatest features is its open-source plugin system. In the Plugin Manager you can install plugins for visualizing how level your bed is, creating magic-like time-lapse videos, catching failures using Artificial Intelligence or remote monitoring/controlling your 3D printer from outside your home network. 

There are hundreds of plug-ins available that do all sorts of things. Check out our post on the [Best OctoPrint Plugins here](https://www.thespaghettidetective.com/blog/2021/09/10/best-octoprint-plugins) to see the most popular OctoPrint plugins and learn how to install them.
