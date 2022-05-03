---
title: OctoPrint Tunneling is now in beta testing
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
tags: ['The Spaghetti Detective Updates', 'OctoPrint']
---

## What is OctoPrint Tunneling?

OctoPrint Tunneling is a secure way to access the full OctoPrint UI even when you are not on your home network.

The Spaghetti Detective provides the access to the most critical functions - webcam feed, pause/cancel, changing heater temperature, etc. However, we understand there are times when you want to access other OctoPrint functions while you are not home, such as using its PSU plugin to turn on/off power supply to your printer.

So we built OctoPrint Tunneling to make it possible for you. 🚀🚀🚀 

## Is OctoPrint Tunneling secure?

<!-- truncate -->

The answer to this question is a resounding **YES**!

We understand the security is you ultimate consideration. Therefore we have built The Spaghetti Detective from ground up with the security as a cornerstone.

Unlike port forwarding, your OctoPrint is never exposed to the wild internet when you access it via TSD's OctoPrint Tunneling. Instead, your OctoPrint page is loaded through an SSL-encrypted tunnel. Nobody can access that tunnel without your TSD account email and password (you didn't share them with anyone did you?).

## How do I access OctoPrint Tunneling?

Easy.

1. Make sure you have upgraded the plugin to version **1.4.0 or higher**.

2. In the printer menu, select "Tunneling".

![](/img/blogs/octoprint-tunnel.png)

## Why does it take so long to load the OctoPrint page in the Tunnel?

This is because, instead of directly loading into your browser, the OctoPrint page has to travel a very long distance through the tunnel.

This is obviously different from other ways to directly access OctoPrint, such as port forwarding, that may expose the traffic to malicious attackers. This is the cost we have to pay to make sure your OctoPrint stays home safely and not catches any virus (literally and metaphorically).

The first time when you use OctoPrint Tunneling, it will be particularly slow because nothing is cached in your browser. However, subsequent uses should be a lot faster since most parts of the OctoPrint page have already been cached.

Please [let us know](mailto:support@thespaghettidetective.com) if OctoPrint Tunneling takes longer than 2 minutes to load on its first time, or longer than 30 seconds on the subsequent uses.

## I got "Webcam stream not loaded" error in OctoPrint!

We have disabled tunneling webcam feed in OctoPrint. The reason for that is OctoPrint uses mjpeg, a very inefficient streaming protocol that takes a lot of bandwidth. We simply can't afford to tunnel this volume of data via our servers.

We urge you to use [TSD's webcam feed](/docs/webcam-streaming-for-human-eyes) instead.

## I found a bug! How can I report it?

Please [email](mailto:support@thespaghettidetective.com) with the detailed description on what the problem is. Please also include the steps leading up to the bug. We will credit your account with 50 non-expirable Detective Hours if we confirm the bug you reported.

## Is OctoPrint Tunneling free?

We don't know yet!

We will definitely make it free for all users **during beta testing period**. In addition to fixing bugs, we will also use the beta testing period to figure out how much OctoPrint Tunneling will cost us to run. We hope the extra cost is marginal and we will happily keep it free forever. However, there is a possibility that the cost is too high for us to absorb, and we may have to make it available only for Pro subscribers, and/or free users with capped usage (similar to how the Detective Hour works).

We will communicate this final decision in our monthly newsletter. Stay tuned and make sure our monthly newsletters don't go to your spam folder!
