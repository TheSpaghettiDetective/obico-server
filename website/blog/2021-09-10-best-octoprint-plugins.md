---
title: The Best OctoPrint Plugins And How To Install Them
author: Neil Hailey
author_url: https://linkedin.com/in/neilhailey/
tags: ['OctoPrint', '3D Printing Tips', 'How-To']
---

[OctoPrint](https://octoprint.org/) is a web interface dedicated to making 3D printing easier by allowing you to control and monitor the process.
The software allows you to access and control virtually any parameter on your printer.

Moreover, in a heart-warming, traditional internet fashion, it’s open source.

There is a vast database of plugins developed by the 3D printing community that make your experience with [OctoPrint](https://octoprint.org/) even better, and here we list and explain the most popular ones.

<!-- truncate -->

## Table of Contents

[Plugin #1: Bed Level Visualizer](#bed_level_visualizer)

[Plugin #2: OctoPrint-PrintTimeGenius](#printtimegenius)

[Plugin #3: Octolapse](#octolapse)

[Plugin #4: DisplayLayerProgress](#displaylayerprogress)

[Plugin #5: Themeify](#themeify)

[Plugin #6: Firmware Updater](#firmware_updater)

[Plugin #7: Navbar Temp](#navbar_temp)

[Plugin #8: Access Anywhere - The Spaghetti Detective](#spaghetti_detective)

[Plugin #9: OctoPrint-Dashboard](#octoprint_dashboard)

[Plugin #10: Creality 2x temperature reporting fix](#creality_temperature_reporting_fix)

[How to get OctoPrint plugins?](#octoprint_plugin_installation)

<a name="bed_level_visualizer">&nbsp;</a>

## Plugin #1: Bed Level Visualizer

Nothing is more important to get the perfect print than your printer’s bed. It’s surface needs to be spotless and levelled. If your printer has a mesh levelling feature, this OctoPrint plugin is one of the best tools for you.

[The Bed Level Visualizer](https://plugins.octoprint.org/plugins/bedlevelvisualizer/) converts data from the bed topography report into a comprehensive 3D map. Thanks to that you get a visualization of the build plate.

![Bed level visualizer](https://plugins.octoprint.org/assets/img/plugins/bedlevelvisualizer/screenshot.png)
*Bed Level Visualizer tab view (Source:[Bed Level Visualizer page on OctoPrint Plugin Repository](https://plugins.octoprint.org/plugins/bedlevelvisualizer/)*

[Check out this user guide video to learn more]( https://www.youtube.com/embed/tyq2hptQXcI).


### **Recommended for:**

- Diagnosing any build plate issues, for example mechanical damage or wrong bed level.

### **Created by:**

[Jneilliii](https://plugins.octoprint.org/by_author/#jneilliii)

[**GitHub page**](https://github.com/jneilliii/OctoPrint-BedLevelVisualizer/)

<a name="printtimegenius">&nbsp;</a>

## Plugin #2: OctoPrint-PrintTimeGenius

Time waits for no one, and every second counts when you have a bunch of prints queuing up.

[PrintTimeGenius](https://plugins.octoprint.org/plugins/PrintTimeGenius/) gives the most accurate estimation of the print time, using both gcode analysers and print history.

The plugin can include the bed and nozzle heating time in its calculations, as well as correct the print time during the process. It promises to get your time right to even seconds!

### **Recommended for:**

- Precise estimation of printing time.

### **Created by:**

[Eyal](https://plugins.octoprint.org/by_author/#eyal)

[**GitHub page**](https://github.com/eyal0/OctoPrint-PrintTimeGenius)

<a name="octolapse">&nbsp;</a>

## Plugin #3: Octolapse

Time lapses are like a dash of magic in our technical world [Octolapse](https://plugins.octoprint.org/plugins/octolapse/) is here to make an enchanting journey out of your print.

The plugin allows to move the extruder out of the frame and position the print bed at the same place each snapshot is taken. All the features are explained in-depth on [the Octolapse project website](https://formerlurker.github.io/Octolapse/)

[Play some copyright-free relaxing music in the background and share it with the world to see!](https://www.youtube.com/embed/54ZKeYPmoVs)

![Octoprint gif](https://media.giphy.com/media/ot9qBu3pIpO3m9cgak/giphy-downsized-large.gif?cid=790b7611dacfd6e1ac2c1992924fb7f870796272c9799d5c&rid=giphy-downsized-large.gif&ct=g)  
Video made with Octolapse by [WitdRoseBuilds](https://www.youtube.com/c/WildRoseBuilds)

### **Recommended for:**

- Making smooth and highly customable time-lapse videos that are a sight to behold.

### **Created by:**

[Brad Hochgesang](https://plugins.octoprint.org/by_author/#brad-hochgesang)

[**GitHub page**](https://github.com/FormerLurker/Octolapse/)

[**Project Homepage**](https://formerlurker.github.io/Octolapse/)

<a name="displaylayerprogress">&nbsp;</a>

## Plugin #4: DisplayLayerProgress

This plugin informs you of print layer progress, estimated end time and current height, all compressed into a simple progress bar.

The information that [DisplayLayerProgress](https://plugins.octoprint.org/plugins/DisplayLayerProgress/) provides can be displayed on OctoPrint’s NavBar and as a tab title or as a pop-up. It even allows you to display progress percentage and current layer on the printer display itself!

![DisplayLayerProgress_bar](https://raw.githubusercontent.com/OllisGit/OctoPrint-DisplayLayerProgress/master/screenshots/statebar.jpg)
*DisplayLayerProgress pop-up (Source: [DisplayLayerProgress](https://plugins.octoprint.org/plugins/DisplayLayerProgress) on OctoPrint Plugin Repository)*

### **Recommended for:**

- Checking printing progress in real time.

### **Created by:**

[Olli](https://plugins.octoprint.org/by_author/#olli)

[ **GitHub page**](https://github.com/OllisGit/OctoPrint-DisplayLayerProgress)

<a name="themeify">&nbsp;</a>

## Plugin #5: Themeify

When you’re done messing with the OctoPrint settings, there’s a room for adding a bit of personality to the interface.

[Themeify](https://plugins.octoprint.org/plugins/themeify/) lets you modify the colour palette and basically any other aspect of the browser display.

![themeify_window](https://plugins.octoprint.org/assets/img/plugins/themeify/discorded_ss.png)
*Discord-inspired Dark Theme for OctoPrint (Source: [Themeify](https://plugins.octoprint.org/plugins/themeify/) on OctoPrint Plugin Repository)*

The community is having a lot of fun with this plugin, so if you’re interested in making your OctoPrint shine like a diamond, be sure to visit [the forum thread](https://community.octoprint.org/t/pimp-my-web-interface/3349/32).

### **Recommended for:**

- Personalized app look, including colour, font types and sizes, etc.

### **Created by:**

[Birk Johansson](https://plugins.octoprint.org/by_author/#birk-johansson)

[**GitHub page**](https://github.com/birkbjo/OctoPrint-Themeify)

<a name="firmware_updater">&nbsp;</a>

## Plugin #6: Firmware Updater

As the title name suggests, this tool updates your printer's firmware from OctoPrint.

Instead of getting printer-specific software or looking for a dedicated flashing program, this smart plugin aggregates many types of firmware, including boards used in Creality and Prusa printers.

[Firmware Updater](https://plugins.octoprint.org/plugins/firmwareupdater/) also allows to customize and configure flashing methods and run a gcode or system command before or after firmware update.

### **Recommended for:**

- Flashing many types of printers and adding pre- or post-flashing commands.

### **Created by:**

[Ben Lye](https://plugins.octoprint.org/by_author/#ben-lye), [Gina Häußge](https://plugins.octoprint.org/by_author/#gina-h%C3%A4u%C3%9Fge), [Nicanor Romero Venier](https://plugins.octoprint.org/by_author/#nicanor-romero-venier)

[**GitHub page**](https://github.com/OctoPrint/OctoPrint-FirmwareUpdater)

<a name="navbar_temp">&nbsp;</a>

## Plugin #7: Navbar Temp

The [Navbar Temp](https://plugins.octoprint.org/plugins/navbartemp/) tool displays bed, nozzle and SoC (Raspberry Pi’s chip) temperature on NavBar.

It is still in development, so as the authors say: “get ready for testing".
![NavBarTemp](https://raw.githubusercontent.com/imrahil/OctoPrint-NavbarTemp/master/images/custom_cmd_cfg1.png)
*NavBar Temp plugin settings window Source: [Navbar](https://plugins.octoprint.org/plugins/navbartemp/) page on OctoPrint Plugin Repository)*

### **Recommended for:**

- Checking temperatures on the printer and Raspberry Pi.

### **Created by:**

[Cosik](https://plugins.octoprint.org/by_author/#cosik), [Jarek Szczepanski](https://plugins.octoprint.org/by_author/#jarek-szczepanski)

[**GitHub page**](https://github.com/imrahil/OctoPrint-NavbarTemp)

<a name="spaghetti_detective">&nbsp;</a>

## Plugin #8: Access Anywhere - The Spaghetti Detective

Okay, I might be a little biased here: I think [The Spaghetti Detective](https://plugins.octoprint.org/plugins/thespaghettidetective/) is super awesome.As a 3D printing enthusiast it makes my life so much easier. Either way, Access Anywhere- The Spaghetti Detective is currently ranked 8 on the most popular OctoPrint Plugins! So what is it?

The Spaghetti Detective, formerly OctoPrint Anywhere, is an all in one plugin that gives you the ability to monitor and control your 3D printer from anywhere with internet connection.  Using the Using Artificial Intelligence, and a webcam or Raspberry Ri camera, it determines whether there’s something wrong going on with your print in real time and can send you a notification or intervene by itself preventing equipment damage and wasted filament.

[Check out the Spaghetti detective in action](https://www.youtube.com/embed/znI9_Vs6X9c). Pay attention to the gauge at the bottom. Video from [the official Spaghetti Detective youtube account](https://www.youtube.com/channel/UCbAJcR6t5lrdZ1JXjPPRjGA).

If it sounds a bit too futuristic, that’s what I thought at first too! While The Spaghetti Detective is still learning, and she does make mistakes, she has already watched over 45,000,000 hours of prints, caught over 575,000 failures and saved over 10,000 spools of filament from being wasted.
Moreover, this plugin gives you the ability to access your webcam from any device, as well as save time-lapses of your prints. A dedicated smartphone app works both on iOS and Android devices.  


![Spaghetti detective](https://plugins.octoprint.org/assets/img/plugins/thespaghettidetective/premium_streaming.gif)  
*Spaghetti Detective phone control panel (Source: [The Spaghetti Detective](https://plugins.octoprint.org/plugins/thespaghettidetective) page on OctoPrint Plugin Repository)*  


However, this plugin has one “but". It’s open source, but to obtain additional features like e-mail support customization of the AI model you have to get a paid subscription from [the official Spahgetti Decetive website](https://www.thespaghettidetective.com).

### **Recommended for:**

- Recognising print fails in real time.

- Getting live feed of the printing process on your phone.

### **Created by:**

[TSD Team](https://plugins.octoprint.org/by_author/#tsd-team)

[**GitHub page**](https://github.com/TheSpaghettiDetective/OctoPrint-TheSpaghettiDetective)

[**Project Homepage**](https://www.thespaghettidetective.com)

<a name="octoprint_dashboard">&nbsp;</a>

## Plugin #9: OctoPrint-Dashboard

[OctoPrint-Dashboard](https://plugins.octoprint.org/plugins/dashboard/) plugin gives you all the basic data of an ongoing print in a user-friendly and informative format.

In general, widgets include:

- Temperatures readout

- Print progress

- Print time

- Current layer and height

- Webcam view

It can be accompanied with [PrintTimeGenius](#printtimegenius) and [DisplayLayerProgress](#displaylayerprogress) explained above.

![octoprint_dasboard](https://plugins.octoprint.org/assets/img/plugins/dashboard/screenshot-2.png)
*Dashboard’s user-friendly display (Source: [OctoPrint-Dashboard](https://plugins.octoprint.org/plugins/dashboard/)  page on OctoPrint Plugin Repository)*

### **Recommended for:**

- Real time overview of a bunch of printing parameters.

### **Created by:**

[Stefan Cohen](https://plugins.octoprint.org/by_author/#stefan-cohen), [j7126](https://plugins.octoprint.org/by_author/#j7126">), [Willmac16](https://plugins.octoprint.org/by_author/#willmac16)

[**GitHub page**](https://github.com/j7126/OctoPrint-Dashboard)

<a name="creality_temperature_reporting_fix">&nbsp;</a>

## Plugin #10: Creality 2x temperature reporting fix

Creality is renowned for making affordable desktop printers, but any Ender or CR series user knows all too well there is much space for improvement (and fun DIY’s!). With the release of v2 line, we receive a set of new “challenges" to overcome.

[Creality 2x temperature reporting fix](https://plugins.octoprint.org/plugins/ender3v2tempfix/) corrects temperature reporting for printers with new mainboard: Ender-3 Pro's, Ender-3 Pro v2, CR-6 SE and others.

### **Recommended for:**

- Fixing readout errors for the new generation of Creality machines.

### **Created by:**

[Albert MN. @ SimplyPrint](https://plugins.octoprint.org/by_author/#albert-mn-simplyprint), [b-morgan](https://plugins.octoprint.org/by_author/#b-morgan)

<a name="octoprint_plugin_installation">&nbsp;</a>

## How to get OctoPrint plugins?

To get the plugins, simply open the links provided, or browse [OctoPrint plugin repository](https://plugins.octoprint.org) by yourself.

The installation process can be done via Plugin Manager built into OctoPrint or with a command line.

Plugin Manager gives 3 options to install a plugin: from the listed plugin repository (using search bar), from URL or from an archive stored in your hardware.

![install plugin octoprint](https://plugins.octoprint.org/assets/img/help/install_plugin_from_repo.png)
*Plugin Manager Browser (Source: [OctoPrint Help](https://plugins.octoprint.org/help/installation/)*)

To install a plugin via command line, paste it into the command line of the host you installed OctoPrint on.

[This wonderful video](https://www.youtube.com/embed/HBd0olxI-No) by [Thomas Sanladerer](https://www.youtube.com/channel/UCb8Rde3uRL1ohROUVg46h1A) can help you get through the process.

For more information see [OctoPrint Help Page](https://plugins.octoprint.org/help/installation/).
