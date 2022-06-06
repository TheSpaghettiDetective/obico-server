---
id: octoprint-tunneling
title: OctoPrint Tunneling
sidebar_label: OctoPrint Tunneling
---

## What is OctoPrint Tunneling?

OctoPrint Tunneling is a secure way to access the full OctoPrint UI even when you are not on your home network

:::note
OctoPrint Tunneling not available for private server users outside of their home network, unless the private server is set up to be accessible from the internet.
:::

## Is OctoPrint Tunneling secure?

The answer to this question is a resounding **YES**!

We understand the security is you ultimate consideration. Therefore we have built Obico from ground up with the security as a cornerstone.

Unlike port forwarding, your OctoPrint is never exposed to the wild internet when you access it via TSD's OctoPrint Tunneling. Instead, your OctoPrint page is loaded through an SSL-encrypted tunnel. Nobody can access that tunnel without your TSD account email and password (you didn't share them with anyone, right?).

## How do I access OctoPrint Tunneling?

Easy.

1. Make sure you have upgraded the plugin to version **1.4.0 or higher**.

2. In the printer menu, select "Tunneling".

![](/img/user-guides/octoprint-tunnel.png)

## Is OctoPrint Tunneling free to all users?

Yes and No. All users can use OctoPrint Tunneling function. However, if you have a Free account, you are limited to tunneling up to 50MB per month. Once you have reached your monthly limit, you won't be able to tunnel to OctoPrint any more until your usage is reset at the beginning of the next month.

The Pro plan subscribers get unlimited tunneling.

## Why is the limit on Free account only 50MB?

We know 50MB is not a lot. The reason why we can't make this cap very high is because we need to temporarily store these data in our high-speed server cache, which is very expensive. In addition, any OctoPrint data tunneled through the Obico Server has to be replicated 4 times. So 50MB data actually means we are charged for 200MB by our cloud provider.

Another reason for this limit is that every time OctoPrint is being loaded via the tunnel, there is a big "spike" of server requests. Therefore, we have to "over-provision" TSD servers to be able to respond to these spikes if multiple users happen to be using OctoPrint Tunneling at the same time. Limiting the usage will help keep the server cost at a reasonable level while still providing a responsive experience anyone who wants to use OctoPrint Tunneling.

The good news is we have optimized our tunneling so that, for any file that has been downloaded to and cached in your browser, you won't need to download again. Therefore, although it'll cost a good chunk of your Free limit when you tunnel to your OctoPrint for the first time, subsequent uses of the tunneling won't take nearly as much. 50MB is sufficient to load OctoPrint 10 to 20 times via the tunnel, which should be good enough for most users in a month. If you need to tunnel to OctoPrint frequently, your best option is to upgrade to the Obico Cloud Pro plan and enjoy unlimited tunneling.

## Why does it take so long to load the OctoPrint page in the Tunnel?

This is because, instead of directly loading into your browser, the OctoPrint page has to travel a very long distance through the tunnel.

This is obviously different from other ways to directly access OctoPrint, such as port forwarding, that may expose the traffic to malicious attackers. This is the cost we have to pay to make sure your OctoPrint is protected from the potential security attacks.

The first time when you use OctoPrint Tunneling, it will be particularly slow because nothing is cached in your browser. However, subsequent uses should be a lot faster since most parts of the OctoPrint page have already been cached.

Please [let us know](/docs/user-guides/contact-us-for-support) if OctoPrint Tunneling takes longer than 2 minutes to load on its first time, or longer than 30 seconds on the subsequent uses.

## It doesn't work for me!

For some users, OctoPrint may fail to load in the tunnel, or the tunnel page remains blank after 60 seconds:

![](/img/user-guides/octoprint_tunneling_blank_page.png)

This is usually caused by a slow internet connection on your Raspberry Pi.

However, all hopes are not lost even if you experience this problem. Please follow the steps below:

1. Refresh the tunneling page using your browser's refresh button. Please do NOT do a "hard-refresh". If you do not know what a "hard-refresh" is, then don't worry. You are not hard-refreshing.

2. Wait for 60 seconds to see if OctoPrint will load this time.

3. If OctoPrint still doesn't load, repeat steps 1 and 2 up to 5 times.

These steps will work for most users who couldn't get OctoPrint to load in the tunnel on the first try. The reason why it works is, again, because OctoPrint Tunneling is optimized for reusing the cache in your browser. So when OctoPrint fails to load on the first try and you refresh the page, the browser doesn't need to download the files that were already downloaded and cached in the browser.

## I got "Webcam stream not loaded" error in OctoPrint!

We have disabled tunneling webcam feed in OctoPrint. The reason for that is OctoPrint uses [M-JPEG](https://en.wikipedia.org/wiki/Motion_JPEG), a very inefficient streaming protocol that takes a lot of bandwidth. We simply can't afford to tunnel this volume of data via our servers.

We urge you to use [Obico's webcam feed](/docs/user-guides/webcam-streaming-for-human-eyes/) instead.
