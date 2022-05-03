---
title: OctoPrint Remote Access
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
description: Port forwarding? VPN? Confused by the different ways for secure remote access your OctoPrint? This guide covers all you need to know.
tags: ['OctoPrint', '3D Printer Remote Access']
---

<head>
  <link rel="canonical" href="https://www.thespaghettidetective.com/blog/2021/09/24/octoprint-anywhere/" />
</head>

:::caution

This post is now out of date. Please check out the [the updated post](/blog/2021/09/24/octoprint-anywhere/).
:::

OctoPrint is one of the best tool you can get for your 3D printer. It provides you with a convenient way to send G-Code to the printer, kick off the print, monitor the print via webcam, and pause/cancel the print all in a beautifully structured user interface.

Once you have indulged yourself in all the great benefits brought forward by OctoPrint, however, you will likely experience a panicking moment when all of the sudden you have lost access to OctoPrint.

That’s right! You can’t access OctoPrint when you are commuting, at work, shopping grocery, or anywhere outside your home wifi network.

<!--truncate-->

## Access OctoPrint remotely when you are not on your home network

Where there is a problem there is a solution. Actually in this case, multiple solutions. We will list the most common options that will bring back the access to OctoPrint in this article. We will also compare and contrast them so that you can decide which one works best for you.

But first of all, let's talk about why you can’t access OctoPrint when you are not on your home network. The reason lies in how your home wifi router works. Your home wifi router connect all of your electronic devices - laptops, ipads, phones, and of course, your Raspberry Pi where OctoPrint runs on. And that is why you can access OctoPrint's web page from your laptop or phone . However, your laptops or phones (when connected to your home wifi) don't directly connect to the internet. Instead, only your wifi router has a direct connection to the internet. All other devices can only access the internet via the wifi router.

<img src="/img/blogs/home-network.png" />

It is like all residents in an apartment building share 1 mailbox. Any residents can send a mail to the rest of the world by putting it in the mailbox. But there is no easy way to send a direct mail to an individual resident.

This is actually a good thing 99% of the times. There are thousands, if not millions,  hackers on the wild internet looking for victims to exploit. And the only reason why your laptops haven't not (hopefully) been attacked is because nobody, including those hackers, can find them because they are "hiding" behind the wifi router. They are invisible to the wild internet. Again the only device on your home network that is directly exposed to the internet is the wifi router. Thankfully all these wifi routers are specially built to fend off the attacks. Therefore, your home network is actually quite safe despite all these hackers on the internet.

However, there is 1% of the times when this becomes a problem. That is when you outside your home network. You pull out the phone and type in *http://octopi.local* but the browser says "oops! can't find the server!". Now you know why you get this error.

Based on what kind of mechanism is utilized to work around this problem, there are 3 different kinds of solutions to help you get access to OctoPrint outside your home network.

If you are too impatient to go through the nitty-gritty details, you can jump straight to the [comparison matrix](#comparison-matrix).

## Direct access

The 1st kind is direct access. To continue using our mailbox analogy, direct access is like making changes to the mailbox or the incoming mails themselves.

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

## Plugin-faciliated remote access

Instead of changing the mailbox or the mail envolope to have a way to delivery incoming mails, this method turns the table and makes use of those outgoing mails to get your access to OctoPrint.

This method requires you to install an OctoPrint plugin. This plugin then pumps webcam feed and printer status to the server running in the cloud (internet). When you are outside your home network and want to access OctoPrint, you connect to the server instead, and the server will pipe the data to your phone.

<img src="/img/blogs/piping-service.png" />

There are quite a few different plugins developed for this purpose. They all share similar pros and cons, since they work on the similar mechansim.

The biggest advantage of plugin-faciliated remote access is it doesn't require any specific knowledge to set up. Although some plugins are a bit easier than others, all of them require these 2 basic steps:

1. Install a plugin. Thanks to the fantastic OctoPrint plugin manager, this step is usually not more than a few clicks of mouse.

1. Sign up an account in the cloud and configure a secure token in the plugin.

The question people often ask is is if plugin-faciliated remote access will be more secure than port forwarding. The answer to this question is a resounding YES. From the diagram above you can see that no special configuration is needed for your home network. Your OctoPrint is still safely hiding behind the wifi router. No one, an attacker can't see your OctoPrint. As a matter of the fact, not even the plugin server in the cloud can see your OctoPrint as it can only passively accept connection from the plugin, not open an unintended connection. Remember, since your OctoPrint is not directly connected to internet, it can only **send**, not **receive** mails (network connections).

The question that is worth a closer look is actually around privacy. Plugin-faciliated remote access works pretty much in the same way as Amazon Echo. So people would naturally have the same privacy concerns as they do with Echo. However, the biggest difference between these plugins and Amazon Echo is that you know exactly what's being sent to the server. The reason for that is, because of the way OctoPrint plugin works, all these plugins have to be open source. So anyone who is concerned about what data are being sent to the server can just take a look at the plugin source code and check it for themselves. Let's take OctoPrint Anywhere as an example, the source code is located [here](https://github.com/kennethjiang/OctoPrint-Anywhere) (this is also where OctoPrint install the plugin from). Anyone who has thoroughly examined the source will conclude the data being sent are:

* Webcam video feed
* Heater temperatures
* Print status such as print time, G-Code file name, etc.
* Printer events such as "print started"

If any of these plugins had dared to eardrop on your wifi network and steal confidential info such as your credit card numbers, it would have been caught hours, or even minutes after the malicious code is released.

The biggest disadvantage of using plugin-faciliated remote access is although it lets you access the most important functions, such as webcam feed and the ability to cancel a print, it doesn't give you access to the original OctoPrint UI. It can occasionally become an issue when, for example, you want to remotely power off the printer using PSU plugin.

I'll list these piping service one by one and comment on the differences between them.

*Disclaimer: I'm the author of OctoPrint Anywhere and The Spaghetti Detective.*

### [OctoPrint Anywhere](https://www.getanywhere.io)

OctoPrint Anywhere is the most popular piping service for OctoPrint. Again I'm the author of OctoPrint Anywhere so I'm probably biased here. But I'll try to stay objective on where I have done a good job at and where I haven't.

#### Pros:

* Easy 1-click setup.
* Free on your first printer.
* Monitor multiple printers on the same screen.
* Mobile-friendly since it was designed to be used on a smart phone to begin with.
* Sharable, 25 frame-per-second true video streaming (paid feature).

#### Cons:

* 25 frame-per-second true video streaming works only on Pi Camera, not USB Cameras such as C270.
* Doesn't provide all the controls, such as sending ad hoc G-Code to printer.

### [The Spaghetti Detective](https://www.thespaghettidetective.com/)

I started The Spaghetti Detective with the sole purpose to catch print failures using AI. But now I have designated it as the successor of OctoPrint Anywhere, simply because The Spaghetti Detective is much better implemented from almost all perspectives - better architecture, faster user experience, more beautiful user interface design, and, of course, the AI that alerts you when your print fails.

### Pros:

* Everything in OctoPrint Anywhere.
* First printer is free.
* It gives you a peach of mind when you are not home. Arguably you don't need remote access any more. ;)
* (Update 09-10-2020) It provides full OctoPrint UI access.

#### Cons:

* Free account has slow webcam feed (1 frame per 10 seconds).
* AI failure detection is limited to 10 hours per month for free account.

### [Telegram](https://plugins.octoprint.org/plugins/telegram/)

Telegram was first piping service avaiable on OctoPrint. It definitely deserves a special mentioning.

#### Pros:

* If you are already using Telegram app, it will integrate with your exiting work flow really well.

#### Cons:

* If you haven't used Telegram before, setting it up can be a daunthing task that involes many steps and some cryptic commands that can easily go wrong.
* There is no webcam feed. You need to enter a command in the chat window just to get the webcam pictured updated. Quite annoying to say the least.
* Limited functions. For instance you can't change the bed or nozzle temperature.

### [Polar Cloud](https://plugins.octoprint.org/plugins/polarcloud/)

#### Pros:

* It's free!
* The functions are heavily geared toward a 3D printing classroom in a school. You are in luck if you are a teacher.
* It has a simple slicer, a catalog of 3D models, so that you directly slice an 3D object and send it to OctoPrint for printing. It lowers the learning curve for beginners such as students.
* It has a print queue that, although isn't very intuitive to use, does function as expected.

#### Cons:

* Linking your OctoPrint to Polar Cloud is tricky to say the least. Be prepared to jump over a few hurdles just to get started.
* The webcam streaming is at extremely low frame rate. I got like 1 frame every **minute** in my test.

### [AstroPrint](https://plugins.octoprint.org/plugins/astroprint/)

#### Pros:

* It's free up to 2 printers.
* Print queue (paid feature)
* Mobile-friendly as it has a native moible app that you can download to your phone.

## Peer-to-peer

The mechanism for how peer-to-peer works is probably the most complicated one, as you can tell from the diagram below. It involes the first "hole-puching" step that, using our mailbox analogy, creates a temporary mailbox. The temporary mailbox is then used as the peer-to-peer (or P2P) communication.

<img src="/img/blogs/peer-to-peer.png" />

It's a myth to say that peer-to-peer doesn't involve a server in the cloud. It does, as you can see from the diagram, except the server is not involved after the first "hole-punching" step.

The most common peer-to-peer solutions are: [TeamViewer](https://www.teamviewer.com/en-us/), [Microsoft Remote Desktop](https://www.microsoft.com/en-us/p/microsoft-remote-desktop/9wzdncrfj3ps?activetab=pivot:overviewtab), [Chrome Remote Desktop](https://remotedesktop.google.com/), and [VNC](https://www.realvnc.com/en/connect/download/viewer/). All of them work on similar mechanism so they share pros and cons:

#### Pros:

* They are either free, or have a free version that's good enough for what we need.
* They are relatively easy to set up and use. No specific technical knowledge is required to get them up and running.

#### Cons:

* You will need a computer running inside your home network in order to access from outside. This most likely means that you need to have a desktop that never sleeps.
* Since the entire screen of your desktop computer will be mapped to your phone screen, it can be extremely awkward and frustrating to use.
* Every time you want to access OctoPrint, you will need to enter the user name and password to authenticate to the remote desktop. This can become really annoying, especially if you are trying to access it from your phone (you most likely are).

## Comparison matrix

| | Easy? | Secure? | Free? | Mobile-friendly? | Video Feed? | OctoPrint UI Access? |
|-|-------|---------|-------|------------------|-----------|----------------------|
| Port Forwarding | <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "orange"}}>Kinda</span> [^1] | <span style={{color: "orange"}}>Kinda</span>[^5] | <span style={{color: "green"}}>Yes</span> |
| VPN | <span style={{color: "red"}}>No</span> | <span style={{color: "orange"}}>Kinda</span>[^5] | <span style={{color: "orange"}}>Kinda</span> [^2] |  <span style={{color: "orange"}}>Kinda</span> [^1] | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> |
| [OctoPrint Anywhere](https://www.getanywhere.io) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "orange"}}>Kinda</span> [^3] |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> |
| [The Spaghetti Detective](https://www.thespaghettidetective.com/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "orange"}}>Kinda</span> [^9] |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |
| [Telegram](https://plugins.octoprint.org/plugins/telegram/) | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [Polar Cloud](https://plugins.octoprint.org/plugins/polarcloud/) | <span style={{color: "red"}}>No</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span>[^6] | <span style={{color: "red"}}>No</span> |
| [AstroPrint](https://plugins.octoprint.org/plugins/astroprint/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "orange"}}>Kinda</span> [^4] |  <span style={{color: "green"}}>Yes</span> | <span style={{color: "red"}}>No</span> | <span style={{color: "red"}}>No</span> |
| [TeamView](https://www.teamviewer.com/en-us/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> [^7]|  <span style={{color: "red"}}>No</span> | <span style={{color: "orange"}}>Kinda</span> [^5] | <span style={{color: "green"}}>Yes</span> |
| [Microsoft Remote Desktop](https://www.microsoft.com/en-us/p/microsoft-remote-desktop/9wzdncrfj3ps?activetab=pivot:overviewtab) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <span style={{color: "orange"}}>Kinda</span> [^5] | <span style={{color: "green"}}>Yes</span> |
| [Chrome Remote Desktop](https://remotedesktop.google.com/) | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <span style={{color: "orange"}}>Kinda</span> [^5] | <span style={{color: "green"}}>Yes</span> |
| [VNC](https://www.realvnc.com/en/connect/download/viewer/) | <span style={{color: "orange"}}>Kinda</span> [^8] | <span style={{color: "green"}}>Yes</span> | <span style={{color: "green"}}>Yes</span> |  <span style={{color: "red"}}>No</span> | <span style={{color: "orange"}}>Kinda</span> [^5] | <span style={{color: "green"}}>Yes</span> |

[^1]: When you are using TouchUI plugin or Printoid.
[^2]: If you set up your own VPN server (such as [PiVPN](http://www.pivpn.io/)), or your router has a built-in VPN. 
[^3]: OctoPrint Anywhere: The first printer is free. $5/month: 2-3 printer. $10/month: unlimited printers.
[^4]: AstroPrint: The first 2 printers are free. $10/month: up to 5 printer; $5/month/printer after that.
[^5]: It's webcam feed embedded in OCtoPrint that refreshes a few times a second but not as smooth as you'd expect from a youtube video.
[^6]: It automatically refreshes the webcam image but the frame rate is so low that it actually makes it a joke.
[^7]: TeamViewer has a paid version but free version is good enough for personal use.
[^8]: Setting up VNC is not as difficult as setup up VPN or even port forwarding, but you will probably need to jump over a few hurdles to get it to work.
[^9]: The Spagehtti Detective: Free account is 1 printer. Pro account: $3/month for first printer. $1.5/month for additional printers.

*Feel free to comment below if I missed anything, or you have your own experience aobut any of these tools.*
