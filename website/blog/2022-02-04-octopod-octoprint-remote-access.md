---
title: "OctoPod Works Anywhere With The Spaghetti Detective’s OctoPrint Tunnel"
author: Neil Hailey
author_url: https://www.linkedin.com/in/neilhailey
author_image_url: "https://cdn-images-1.medium.com/fit/c/300/300/1*L2wRkwCzzk4_YQ6WplroVg.png"
tags: ['Tech', '3D Printer Remote Access', 'OctoPrint', '3D Printing Tips', 'how-to']
---

[OctoPod](https://apps.apple.com/us/app/octopod-for-octoprint/id1412557625) is a popular iOS mobile app for accessing your OctoPrint connected printer with your phone so you can now use the app from anywhere for free! Learn more about the integration below:



![OctoPod App](/img/blogs/octopod/OctoPod_Panel.png)

Source: [OctoPod Github](https://github.com/gdombiak/OctoPod)

<!--truncate-->

## What is OctoPod?

  ![OctoPod](/img/blogs/octopod/octopod.png)

Source: [Apple](https://apps.apple.com/us/app/octopod-for-octoprint/id1412557625)

OctoPod is a popular iOS mobile app for accessing your OctoPrint connected printer with your phone. While the full OctoPrint interface is great on desktop devices, it can be quite a pain to access it on a mobile device. The layout is not very mobile-friendly, so you may find yourself having to zoom in and out quite often. There are a few OctoPrint plugins like Touch UI, that help make the OctoPrint interface more mobile-friendly, but, there are also some great mobile apps that are dedicated to providing a clean interface to monitor and control OctoPrint connected printers.

OctoPod is a popular choice among makers for using OctoPrint on a mobile device. One of the most compelling features about OctoPod is it’s completely free! Once you connect one or multiple printers to the app, you’ll be able to check in on the printer's webcam stream, set and monitor temperatures, start prints, and so much more - OctoPod’s feature list is seemingly endless! You can even use Siri to control your printer with this app!



## Accessing OctoPod (and OctoPrint) When Away From Home

![OctoPod App Printer Screen](/img/blogs/octopod/printing.PNG)

A situation arises when you are away from home, and you are unable to access OctoPod. This happens because OctoPrint only works when you are on the same network as your raspberry pi or other device running OctoPrint. Maybe you’re at work, running a complex print at home, and you want to check in on your print! Well, if you are using The Spaghetti Detective’s Ai failure detection, there’s a good chance you’ll have the peace of mind you need to work without checking on your print, but maybe you want to just check to make sure everything is looking okay still, well now you can! For free! The Spaghetti Detective has partnered with OctoPod to make OctoPod work anywhere. With the free plan, you’ll get up to 50MB of tunneling access (The “tunnel” is The Spaghetti Detective’s feature that allows you to access OctoPrint remotely from outside of the local network). Pro Plan users of The Spaghetti Detective get unlimited tunneling access.



## How Do You Link OctoPod and The Spaghetti Detective?



Once you have downloaded OctoPod from the App Store, [follow these instructions](https://github.com/gdombiak/OctoPod/wiki/How-to-add-new-printers-to-OctoPod%3F) to link your printer to OctoPod. If you don’t already have an account with The Spaghetti Detective, [follow this guide](https://www.thespaghettidetective.com/docs/user_guides/octoprint-plugin-setup/) to set up The Spaghetti Detective.


At this point, you should have a printer linked to OctoPod you created an account with The Spaghetti Detective and linked the OctoPrint Plugin. To link The Spaghetti Detective with OctoPod, complete the following steps:



1.  Open OctoPod.

2.  Go to the settings screen.

3.  Select the printer that you want to be able to access remotely.

4.  Copy the API key as shown, then click back.


![Copy API Key](/img/blogs/octopod/copy_api.PNG)

5.  Click the plus  sign to add a printer, and then click The Spaghetti Detective

6.  Sign into your The Spaghetti Detective account, select the printer you are linking, and then click authorize.


  ![Autorize App](/img/blogs/octopod/authorize.PNG)

7.  Name the printer, and then paste the previously copied API key as shown.

    ![Paste API key](/img/blogs/octopod/paste-code.PNG)

9.  Click save.

You can now access this printer from anywhere with OctoPod thanks to The Spaghetti Detective's OctoPrint tunneling. While using the tunneling feature, the stream will be a lower framerate to save bandwidth.



An example of a connected printer is shown below: ![Remote 3D Printer Monitoring](/img/blogs/octopod/printing.PNG)


