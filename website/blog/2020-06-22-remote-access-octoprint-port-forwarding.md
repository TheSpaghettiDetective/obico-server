---
title: A Step-by-step Guide to Set Up Port-forwarding for OctoPrint Remote Access
author: Luke's Laboratory
author_url: https://twitter.com/LukesLaboratory
author_image_url: https://pbs.twimg.com/profile_images/1095154617774616576/MlQbHJSm_400x400.jpg
description: A detailed guide for setting up port forwarding for OctoPrint remote access. It also discusses the security risk around port forwarding.
tags: ['OctoPrint', '3D Printer Remote Access']
---

Port-forwarding is a technique that gives you access to your OctoPrint from anywhere on the internet, not just when you are on your home network. This guide will walk you through the process step-by-step to show you how to set it up.

**Important note: Port-forwarding may be a potential security risk for your home network. Please avoid it unless you know what risks you are taking by setting up port-forwarding. You may want to check [other options for accessing OctoPrint from the internet](/blog/2019/08/24/octoprint-remote-access).** 

<!--truncate-->

## Why Port-forwarding?

We’re still staying home far more than the norm, but for those who are still out and about and wanting to check your print to make sure its on-task or to see if you even started the print, a common question is “how do I connect when I’m not on my home internet?”

You’re able to connect to it at home using a web browser and navigating to the simple IP address: 192.168.0.XXX; but, when you try to connect to that on the go, you get a 404, address not found error. The reason is simple – your Raspberry Pi and OctoPrint server, while completely accessible at home, is not exposed to the wider web. That is, Your OctoPrint is only accessible on your local area network (LAN), but not accessible to the world-wide web (WAN – Wide Area Network). Your router serves as the gatekeeper that connects your LAN to the WAN, but also makes sure that your LAN isn’t accessible to everyone on the web for your security and privacy. Its also used to make sure that your internal network doesn’t request individual IP’s on the WAN (Which is why all of your home devices typically take the IP address of (192.168.0.XXX) but you only have one WAN IP. 

So what do you need to do to connect your Raspberry Pi to the rest of the world? Well, you’ll need to forward exterior requests for webpages (what your web browser is looking for) to your Pi. Specifically, you’ll need to instruct your router to forward requests for port 80 (HTTP) to the Pi on your LAN.

What is a port? A port is a specific endpoint for traffic, normally used for separating data flows and allowing multiple different forms of communication to be easily sorted to a single IP.  There are unique ports typically used for webpages, email, Minecraft, SSH, file transfer, and many, many other applications. The port that we will specifically be using will be port 80, which is the default for HTTP traffic, which is what is used for loading webpages in your browser. 

## Prerequisites

In order to forward the port to your Pi, you’ll need to know a few things:

1.	Your router’s
    * IP address
    * Username+Password
2.	Your external IP address
3.	Your Raspberry Pi’s IP address on your LAN.

## Find out your router’s IP address

As for your router’s IP address, the simplest way of trying to find it is to attempt to access common home router IP’s such as 192.168.0.1 or 192.168.1.1.

Alternatively, you can try to open up the command prompt (for windows) and run the command `ip config` – the “default gateway” provided will very likely be your router’s ip.

## Log in your router with username and password

Open your router's IP address in a web browser, and you’ll likely come across a login screen similar to the one shown below. If you know your username and password, GREAT! If you don’t, the default may be in the manual or on the side of the router. If you can’t find the manual/not on a sticker, try googling your model with the default password. If the default doesn’t work, you may be out of luck unless you do a hard reset to bring everything back to stock. If the default does work, I recommend changing the default user and password to grant a more secure interface.

![](/img/blogs/port-forwarding-1.png)

**CAUTION – DO NOT DO THIS UNLESS YOU KNOW HOW TO RE-SETUP YOUR SERVICE, AS YOU MAY LOSE CONNECTION IF YOUR ROUTER WAS MANAGING AUTHENTICATION.**

## Find out your external IP address

Once you’re logged in, you’ll likely be greeted by a generic info screen, similar to the below:

![](/img/blogs/port-forwarding-2.png)

Thankfully, my router is generous enough to give me item #2 on our list, the external IP of the router. This is the address that the rest of the world can use to contact your entire home network, and how your traffic appears to others. We’ll use this later. Depending on your ISP, this may or may not be fixed. My provider has a super-stable IP that only changes when I reboot my router, but others may use a constantly rotating IP. Dynamic DDNS will be required if this is the case, but is outside of the purview of this guide. 

If your router doesn’t provide this information, a simple search on google for “what is my IP” should provide the same information.

![](/img/blogs/port-forwarding-3.png)


## Find out your Raspberry Pi’s IP address

If you already know your Raspberry Pi's IP address, you can skip this step.

Otherwise, I assume you are access your OctoPrint using a name like `octopi.local`. If this is the case, you can find out its IP address by:

1. SSH to your Raspberry Pi. Here is how to do it on [Windows](https://www.raspberrypi.org/documentation/remote-access/ssh/windows10.md), [Mac](https://www.raspberrypi.org/documentation/remote-access/ssh/unix.md), and [Linux](https://www.raspberrypi.org/documentation/remote-access/ssh/unix.md).
2. Run command `ip addr`. You can find the IP address in the output, as shown in this screenshot.

![](/img/blogs/port-forwarding-4.png)

## Finally, set up port-forwarding!

The “basic” tab that I’m given doesn’t have the settings I’m looking for. This may differ on your particular router. 

Opening the Advanced tab and I get quite a bit more information. 

![](/img/blogs/port-forwarding-5.png)

What I’m going to be looking for is “port forwarding” which I expect to be in the security or NAT (Network Address Translation) forwarding sections. 


![](/img/blogs/port-forwarding-6.png)


By trial-and-error, I find “virtual servers” which holds some port forwards I have already filled out.

![](/img/blogs/port-forwarding-7.png)

As you can see, there are several fields – Service Type, which is just a description of the service, external port (which is the port that the WAN will see) internal IP (which is where the external port’s traffic will be directed to), internal port (where the port will be rerouted to, can be different than the external port) and the protocol.

To add it, I hit the “add” button (who’d a thunk) and am greeted with the form below.

![](/img/blogs/port-forwarding-8.png)

Fill in the form! If you’d like an extra layer of obfuscation, its perfectly acceptable to make your external port 42069 or whatever you’d like, and still route it to internal port 80, all it would mean is that when you enter your WAN IP into your browser, you’ll have to add :42069 to the end before you hit enter. It’ll still work just the same. 

![](/img/blogs/port-forwarding-9.png)


Once you have added the entry, it will appear just like the other entries in the table: 

![](/img/blogs/port-forwarding-10.png)



Once this is added, you should now be able to access your OctoPrint session from a device not hooked up to your local network. Try this on a phone with the wifi disabled – open the browser, and CAREFULLY type in the external IP from earlier. If you specified a custom port (NOT 80) you’ll need to append :custom_port as described earlier.

If successful, you should be greeted with the login for OctoPrint! From here, you should be able to log in and do all the things that you could do from home, from wherever in the world!

I’ve tried to be as generic as possible with this guide, making sure to use the language that is easily searchable should your router be labelled differently. Many possible permutations can be solved with “router_model port forward” and filling in similar information as described here.

Let us know if this guide helped you and if you have any questions!

**IMPORTANT:**

**AGAIN, BY EXPOSING YOUR PRINTER TO THE WIDER WEB, YOU MAY BE EXPOSING YOURSELF TO MALICIOUS ATTACKS THAT MAY DAMAGE YOUR EQUIPMENT. PLEASE BE CAREFUL AND USE STRONG PASSWORDS TO PROTECT YOUR PRINTER/HOME.**

