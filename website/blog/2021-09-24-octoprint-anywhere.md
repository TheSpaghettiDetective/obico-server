---
title: "OctoPrint Anywhere: Accessing OctoPrint Remotely"
author: Neil Hailey
author_url: https://www.linkedin.com/in/neilhailey
author_image_url: "https://cdn-images-1.medium.com/fit/c/300/300/1*L2wRkwCzzk4_YQ6WplroVg.png"
tags: ['Tech', '3D Printer Remote Access', 'OctoPrint', 'How-to']
---

:::note

This is an update on [the original post](/blog/2019/08/24/octoprint-remote-access/).
:::

[OctoPrint](https://octoprint.org/) is one of the best tools you can get for your 3D printer. It provides you with a convenient way to send G-Code to the printer, kick off the print, monitor the print via webcam, and pause/cancel the print all in a beautifully structured user interface. There is a downside though - OctoPrint can only be accessed on your home network, not anywhere else.

Imagine: you just set up a print, turned the printer on, and see everything is perfect. You have some spare time so you leave the house, but one thought lingers – what’s going on with my print? Did it fail, how much time there is left for it to end?

No need to panic. Although you can't **directly** use OctoPrint outside your home network, there are plenty of ways to let you do that **indirectly** from anywhere as long as you have an Internet connection. It may be hard to choose which option is the best for you. In this article we try to help you with that, presenting the pros and cons of all possible ways to access your printer remotely.

<!--truncate-->

## Ways to access OctoPrint anywhere with an Internet connection

If you are in a hurry, here's a list of all available software and methods to give you access to your OctoPrint from anywhere as long as you have an Internet connection.

However, we strongly recommend you spend the time to go over this article to understand what all these pros and cons mean to you so that you can make an informed decision about which tool fits your needs the best.


| | Easy? | Secure? | Free? | Mobile-friendly? | Video Feed? | OctoPrint UI Access? |
|-|-------|---------|-------|------------------|-----------|----------------------|
| [The Spaghetti Detective](https://www.thespaghettidetective.com/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote9" style={{color: "orange"}}>Kinda<span className="superscript">[9]</span></a> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |
| [OctoPrint Anywhere](https://www.getanywhere.io) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote3" style={{color: "orange"}}>Kinda<span className="superscript">[3]</span></a> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> |
| [Polar Cloud](https://plugins.octoprint.org/plugins/polarcloud/) | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <a href="#footnote6" style={{color: "red"}}>No<span className="superscript">[6]</span></a> | <span style={{color: "red"}}>No</span> |
| [SimplyPrint](https://simplyprint.io/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote12" style={{color: "orange"}}>Kinda<span className="superscript">[12]</span></a> |  <span style={{color: "green"}}>Yes</span> | <a href="#footnote13" style={{color: "orange"}}>Kinda<span className="superscript">[13]</span></a> | <span style={{color: "red"}}>No</span> |
| [Raisecloud](https://cloud.raise3d.com/raise3d.html) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote11" style={{color: "orange"}}>Kinda<span className="superscript">[11]</span></a> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [AstroPrint](https://plugins.octoprint.org/plugins/astroprint/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote4" style={{color: "orange"}}>Kinda<span className="superscript">[4]</span></a> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [OctoEverywhere](https://octoeverywhere.com/dashboard) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote10" style={{color: "orange"}}>Kinda<span className="superscript">[10]</span></a> | <a href="#footnote1" style={{color: "orange"}}>Kinda<span className="superscript">[1]</span></a> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| [Ngrok Tunnel](https://plugins.octoprint.org/plugins/ngrok/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote1" style={{color: "orange"}}>Kinda<span className="superscript">[1]</span></a> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| Port Forwarding | <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> |  <a href="#footnote1" style={{color: "orange"}}>Kinda<span className="superscript">[1]</span></a> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| VPN | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote2" style={{color: "orange"}}>Kinda<span className="superscript">[2]</span></a> |  <a href="#footnote1" style={{color: "orange"}}>Kinda<span className="superscript">[1]</span></a> | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> |
| [Telegram](https://plugins.octoprint.org/plugins/telegram/) | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [OctoPrint DiscordRemote](https://plugins.octoprint.org/plugins/DiscordRemote/) | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [TeamView](https://www.teamviewer.com/en-us/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <a href="#footnote7" style={{color: "green"}}>Yes<span className="superscript">[7]</span></a> |  <span style={{color: "red"}}>No</span> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| [Microsoft Remote Desktop](https://www.microsoft.com/en-us/p/microsoft-remote-desktop/9wzdncrfj3ps?activetab=pivot:overviewtab) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| [Chrome Remote Desktop](https://remotedesktop.google.com/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |
| [VNC](https://www.realvnc.com/en/connect/download/viewer/) | <a href="#footnote8" style={{color: "orange"}}>Kinda<span className="superscript">[8]</span></a> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <a href="#footnote5" style={{color: "orange"}}>Kinda<span className="superscript">[5]</span></a> | <span style={{color: "green"}}>Yes</span> |

<div style={{fontSize: "0.9em", fontStyle: "italic"}}>
<div id="footnote1">[1] When you are using TouchUI plugin or Printoid.</div>
<div id="footnote2">[2] If you set up your own VPN server (such as [PiVPN](http://www.pivpn.io/)), or your router has a built-in VPN.</div>
<div id="footnote3">[3] OctoPrint Anywhere: The first printer is free. $5/month: 2-3 printer. $10/month: unlimited printers.</div>
<div id="footnote4">[4] AstroPrint: The first 2 printers are free. $10/month: up to 5 printer; $5/month/printer after that.</div>
<div id="footnote5">[5] It's webcam feed embedded in OCtoPrint that refreshes a few times a second but not as smooth as you'd expect from a youtube video.</div>
<div id="footnote6">[6] It automatically refreshes the webcam image but the frame rate is so low that it's more like a joke.</div>
<div id="footnote7">[7] TeamViewer has a paid version but free version is good enough for personal use.</div>
<div id="footnote8">[8] Setting up VNC is not as difficult as setup up VPN or even port forwarding, but you will probably need to jump over a few hurdles to get it to work.</div>
<div id="footnote9">[9] The Spaghetti Detective: Free account: up to 1 printer. Pro account: $4/month for first printer. $2/month for additional printers.</div>
<div id="footnote10">[10] OctoEverywhere: $2.49-4.99/mo basic perks; $7.99-11.99/mo elite perks;</div>
<div id="footnote11">[11] RaiseCloud: users will need to purchase support for more than one printer, the price is not yet determined;</div>
<div id="footnote12">[12] SimplyPrint: $5.99/mo basic, $9.99/mo pro;</div>
<div id="footnote13">[13] SimplyPrint's document claims 1 FPS webcam stream. But it didn't work when I tested it.</div>
</div>

## Why can't I use OctoPrint anywhere but on my home network?

To fully understand the pros and cons presented in the matrix above, you need to understand why OctoPrint can't be accessed outside your home network.

The reason lies in how the wifi router works. Your wifi router connect all of your electronic devices - laptops, ipads, phones, and of course, your Raspberry Pi where OctoPrint runs on. And that is why you can access OctoPrint's web page from your laptop or phone . However, your laptops or phones (when connected to your home wifi) don't directly connect to the internet. Instead, only your wifi router has a direct connection to the internet. All other devices can only access the internet via the wifi router.

<img src="/img/blogs/home-network.png" />

It is like all residents in an apartment building share 1 mailbox. Any residents can send a mail to the rest of the world by putting it in the mailbox. But there is no easy way to send a direct mail to an individual resident.

This is actually a good thing. There are thousands, if not millions,  hackers on the wild internet looking for victims to exploit. And the only reason why your laptops haven't not (hopefully) been attacked is because nobody, including those hackers, can find them because they are "hiding" behind the wifi router. They are invisible to the wild internet. Again the only device on your home network that is directly exposed to the internet is the wifi router. Thankfully all these wifi routers are specially built to fend off the attacks. Therefore, your home network is actually quite safe despite all these hackers on the internet.

However, there are circumstances when this becomes a problem. That is when you outside your home network. You pull out the phone and type in *http://octopi.local* but the browser says "oops! can't find the server!". Now you know why you get this error.

Based on what kind of mechanism is utilized to work around this problem, there are 3 different kinds of solutions to help you get access to OctoPrint outside your home network.

- [Direct access](#direct-access)

- [Plugin-facilitated remote access](#plugin-facilitated-remote-access)

- [Peer-to-peer network](#peer-to-peer-network)

## Direct access

The 1st kind is direct access. To continue using our mailbox analogy, direct access is like making changes to the mailbox or the incoming mails themselves.

It’s pretty complicated if you want to keep it safe and secure - there’s no 3rd party service to do it for you. If you don’t provide any layer of security yourself, you open the door your yourself as well as others - any hacker can send something malicious to your OctoPrint, which is not built to defend this kind of attack.

### Port Forwarding

Port forwarding is like attaching a smaller mailbox to the original mailbox. In this case, the smaller mailbox will be dedicated to the Raspberry Pi and everything going in there will be directed to OctoPrint running in the Pi.

<img src="/img/blogs/port-forwarding.png" />

This smaller mailbox is called "a port" in networking terms.

The biggest advantages about port forwarding are it doesn't cost you any money and it is quite easy to do. You don't need to be a networking expert to figure it out. Instead, you only need to make some configuration changes to your wifi router to by using its management console. And most modern wifi routers have made this task relatively painless.

For this reason, port forwarding used to be, and probably still is, most commonly used to get access to OctoPrint from outside the home network. However, as you can probably tell, the biggest problem with this approach is it completely defeats the layer of security protection we mentioned earlier. Any hacker can drop a malicisous mail into this smaller mailbox and get it delivered to your OctoPrint, which is not built to defend this kind of attack.

In fact, [more and more people have started to realize the potential security risk](https://isc.sans.edu/forums/diary/3D+Printers+in+The+Wild+What+Can+Go+Wrong/24044/) of port forwarding and ditched it in favor of other options.

### VPN

At high level, VPN provides something similar to port forwarding - it provides a way to get mails delivered to individule resident. It is just that, instead of changing the mailbox, VPN changes the mail envolope. It's similar to putting another envolope that says "attn: OctoPrint" inside the outer one.

"Wait!" I can hear you saying, "why can't hackers also doubly-envolope their mailicious mails and get them delivered to OctoPrint in the same way?". Good question! The answer lies in the fact that the inner envolope is not only addressed, but also digitally signed and encrypted. When configured properly, VPN can be as secure as the HTTPS connection to your bank's website.

However, this extra layer of security is exactly what causes VPN to be quite difficult to set up. Only very high-end home wifi routers come with built-in VPN server. And even with that, setting it up is no small feat. Most wifi routers on the market today at best can only work with an external VPN server, which usually costs extra monthly fees and significantly slows down your internet speed.


## Plugin-facilitated remote access

Instead of changing the mailbox or the mail envolope to have a way to delivery incoming mails, this method turns the table and makes use of those outgoing mails to get your access to OctoPrint.

This method requires you to install an OctoPrint plugin. This plugin then pumps webcam feed and printer status to the server running in the cloud (internet). When you are outside your home network and want to access OctoPrint, you connect to the server instead, and the server will pipe the data to your phone.

<img src="/img/blogs/piping-service.png" />


There are quite a few different plugins developed for this purpose. They all share similar pros and cons since they work on a similar mechanism.

The biggest advantage of plugin-facilitated remote access is it doesn’t require any specific knowledge to set up. Although some plugins are a bit easier than others, all of them require these 2 basic steps:

1.  Install a plugin. Thanks to the fantastic OctoPrint plugin manager, this step is usually not more than a few clicks of the mouse.
2.  Sign up for an account in the cloud and configure a secure token in the plugin.

The question people often ask is if plugin-facilitated remote access will be more secure than port forwarding. The answer to this question is a resounding YES. From the diagram above you can see that no special configuration is needed for your home network. Your OctoPrint is still safely hiding behind the wifi router. No one, not even an attacker can see your OctoPrint. As a matter of the fact, not even the plugin server in the cloud can see your OctoPrint as it can only passively accept connections from the plugin, not open an unintended connection. Remember, since your OctoPrint is not directly connected to the internet, it can only **send**, not **receive** mails (network connections).

The question that is worth a closer look at is actually around privacy. Plugin-facilitated remote access works pretty much in the same way as Amazon Echo. So people would naturally have the same privacy concerns as they do with Echo. However, the biggest difference between these plugins and Amazon Echo is that you know exactly what’s being sent to the server. The reason for that is, because of the way the OctoPrint plugin works, all these plugins have to be open source. So anyone who is concerned about what data are being sent to the server can just take a look at the plugin source code and check it for themselves. Let’s take OctoPrint Anywhere as an example, the source code is located [here](https://github.com/kennethjiang/OctoPrint-Anywhere). The Spaghetti Detective took one step further to not only open source [the plugin code](https://github.com/TheSpaghettiDetective/OctoPrint-TheSpaghettiDetective) but also [the server code](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective). Anyone who has thoroughly examined the source will conclude the data being sent are:

* Webcam video feed
* Heater temperatures
* Print status such as print time, G-Code file name, etc.
* Printer events such as "print started"

If any of these plugins had dared to eardrop on your wifi network and steal confidential info such as your credit card numbers, it would have been caught days, or even hours after the malicious code is released.

The biggest disadvantage of using plugin-facilitated remote access is although most of the plugins let you access the most important functions, such as webcam feed and the ability to cancel a print, they don't give you access to the original OctoPrint UI. It can become an issue when, for example, you want to remotely power off the printer using PSU plugin.

I'll list the most popular piping service one by one and comment on the differences between them.

- [The Spaghetti Detective](#the-spaghetti-detective)
- [OctoPrint Anywhere](#octoprint-anywhere)
- [AstroPrint](#astroprint)
- [RaiseCloud](#raisecloud)
- [OctoEverywhere](#octoeverywhere)
- [Polar Cloud](#polar-cloud)
- [SimplyPrint](#simplyprint)
- [Ngrok Tunnel](#ngrok-tunnel)
- [Telegram](#telegram)
- [OctoPrint DiscordRemote](#octoprint-discordremote)

:::note
Disclaimer: I am a team member behind The Spaghetti Detective and OctoPrint Anywhere.
:::

### [The Spaghetti Detective](https://www.thespaghettidetective.com/)

The Spaghetti Detective and OctoPrint Anywhere have been merged into one, sustaining features of the both. It’s still [the most popular OctoPrint remote access plugin](https://plugins.octoprint.org/plugins/thespaghettidetective/) to this day - you can not only stream the video feed from your camera, but also gain remote access to the printer with your phone, and even have fail detection notifications sent to your device.


#### Pros:

* Easy 1-click setup.
* Free on your first printer.
* Monitor multiple printers on the same screen.
* Mobile-friendly since it was designed to be used on a smartphone to begin with: Mobile apps are available on Android and iOS.
* Sharable, 25 frame-per-second true video streaming, remote uploading, and printing G-code (paid features).
* It gives you a peach of mind when you are not home. Arguably you don't need remote access anymore. ;)
* It provides full OctoPrint UI access.

#### Cons:

* Free account has slow webcam feed (1 frame per 10 seconds).
* AI failure detection is limited to 10 hours per month for a free account.

### [OctoPrint Anywhere](https://www.getanywhere.io)

OctoPrint Anywhere is the predecessor of The Spaghetti Detective and is now in maintenance mode. You are highly encouraged to use The Spaghetti Detective instead.

#### Pros:

* Easy 1-click setup.
* Free on your first printer.
* Monitor multiple printers on the same screen.
* Mobile-friendly since it was designed to be used on a smartphone, to begin with.
* Sharable, 25 frame-per-second true video streaming (paid feature).

#### Cons:

* 25 frame-per-second true video streaming works only on Pi Camera, not USB Cameras such as C270.
* Doesn't provide all the controls, such as sending ad hoc G-Code to a printer.


### [AstroPrint](https://plugins.octoprint.org/plugins/astroprint/)

#### Pros:

* It's free up to 2 printers.
* Print queue (paid feature)
* Mobile-friendly as it has a native mobile app that you can download to your phone.


### [RaiseCloud](https://cloud.raise3d.com/raise3d.html)

RaiseCloud is a management platform dedicated to their own printers to manage, monitor, and process 3D prints. It’s mostly aimed at printing farms.

#### Pros:

*   Stopping and starting prints, viewing the webcam, control all the settings during a print for adjustments for many printers at once.
*   IdeaMaker integration.

#### Cons:

*   [RaiseCloud OctoPrint plugin](https://plugins.octoprint.org/plugins/raisecloud/) offers only one printer support, so it makes more sophisticated management options inaccessible on OctoPi.

### [OctoEverywhere](https://octoeverywhere.com/dashboard)

#### Pros:

*   Full access to OctoPi UI.
*   20MB free space for upload/download for your disposal.
*   Sharable links if you want video streaming or a 3rd party access to your printer (paid feature).
*   Integration with 3rd party OctoPi apps for Android and iOS (paid feature).
*   You can upgrade to a paid version for more free space (up to 900 MB), up to 10 printers access, and longer webcam streaming

#### Cons:

*   Doesn’t have its own smartphone app and 3rd party app integration is hidden under a paywall.
*   Webcam feed is full-resolution but with strictly limited duration.
*   Maximum of 10 printers even in the subscription program.
*   As paid accounts have streaming/access priority and the plugin is gaining traffic, there may be some connection issues for free users.

### [Polar Cloud](https://plugins.octoprint.org/plugins/polarcloud/)

#### Pros:

* It's free!
* The functions are heavily geared toward a 3D printing classroom in a school. You are in luck if you are a teacher.
* It has a simple slicer, a catalog of 3D models so that you directly slice a 3D object and send it to OctoPrint for printing. It lowers the learning curve for beginners such as students.
* It has a print queue that, although isn't very intuitive to use, does function as expected.

#### Cons:

* Linking your OctoPrint to Polar Cloud is tricky, to say the least. Be prepared to jump over a few hurdles just to get started.
* The webcam streaming is at an extremely low frame rate. I got like 1 frame every **minute** in my test.

### [SimplyPrint](https://simplyprint.io/)


#### Pros:

*   Many anti-fail features, like filament tracking and bed leveling.
*   Simple built-in slicer.
*   [Free version](https://plugins.octoprint.org/plugins/SimplyPrint/) can support 2 printers and you can have 1GB storage space for your files.
*   SMS notifications, stats, and other features in a paid subscription.

#### Cons:

*   “Streaming” with maximum framerate of 1 FPS for $10 (!).

### [Ngrok Tunnel](https://plugins.octoprint.org/plugins/ngrok/)

This plugin is a purely technical feature to create proxy tunnels via [ngrok](https://ngrok.com) service.

#### Pros:

*   Proxy tunnel for OctoPI with SSL and basic authentication gives you a secure connection.
*   You can get basically everything out of your OctoPi if your Internet connection is good enough.

#### Cons:

*   This is just setting up OctoPi remote connection, so no interface or special features - for advanced users.
*   Free version can support a single printer only and is set up on a random subdomain that changes every time OctoPi is restarted. You can upgrade for more printers and reserved domains, but every one of them will have a separate tunnel.

### [Telegram](https://plugins.octoprint.org/plugins/telegram/)[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#telegram)

Telegram was the first piping service available on OctoPrint. It definitely deserves a special mentioning.

#### Pros:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#pros-8)

-   If you are already using the Telegram app, it will integrate with your existing workflow really well.

#### Cons:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#cons-7)

-   If you haven't used Telegram before, setting it up can be a daunting task that involves many steps and some cryptic commands that can easily go wrong.
-   There is no webcam feed. You need to enter a command in the chat window just to get the webcam pictured updated. Quite annoying to say the least.
-   Limited functions. For instance, you can't change the bed or nozzle temperature.

### [OctoPrint DiscordRemote](https://plugins.octoprint.org/plugins/DiscordRemote/)[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#octoprint-discordremote)

Discord is a new popular kid in the online communication world. It’s a modern twist on a classic IIRC - you can set up your own channel and invite friends, with conversations stored in separate chatrooms. With [OctoPrint DiscordRemote](https://plugins.octoprint.org/plugins/DiscordRemote/) and a bot, you can start/stop the print, list files, take a cam snapshot to display within Discord.

#### Pros:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#pros-9)

-   Useful for a quick notification if you’re frequently using Discord.

#### Cons:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#cons-8)

-   Same as Telegram, you have to set up a server and use commands, while it gives you little control over the print process.

## Peer-to-peer network[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#peer-to-peer-network)

The mechanism for how peer-to-peer works is probably the most complicated one, as you can tell from the diagram below. It involves the first "hole-punching" step that, using our mailbox analogy, creates a temporary mailbox. The temporary mailbox is then used as peer-to-peer (or P2P) communication.

<img src="/img/blogs/peer-to-peer.png" />

It's a myth to say that peer-to-peer doesn't involve a server in the cloud. It does, as you can see from the diagram, except the server is not involved after the first "hole-punching" step.

The most common peer-to-peer solutions are [TeamViewer](https://www.teamviewer.com/en-us/), [Microsoft Remote Desktop](https://www.microsoft.com/en-us/p/microsoft-remote-desktop/9wzdncrfj3ps?activetab=pivot:overviewtab), [Chrome Remote Desktop](https://remotedesktop.google.com/), and [VNC](https://www.realvnc.com/en/connect/download/viewer/). All of them work on similar mechanisms so they share pros and cons:

#### Pros:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#pros-10)

-   They are either free or have a free version that's good enough for what we need.
-   They are relatively easy to set up and use. No specific technical knowledge is required to get them up and running.

#### Cons:[#](https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere#cons-9)

-   You will need a computer running inside your home network in order to access it from outside. This most likely means that you need to have a desktop that never sleeps.
-   Since the entire screen of your desktop computer will be mapped to your phone screen, it can be extremely awkward and frustrating to use.
-   Every time you want to access OctoPrint, you will need to enter the user name and password to authenticate to the remote desktop. This can become really annoying, especially if you are trying to access it from your phone (you most likely are).
