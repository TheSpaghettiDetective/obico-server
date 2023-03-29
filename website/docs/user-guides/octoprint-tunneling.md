---
id: octoprint-tunneling
title: OctoPrint/Klipper Tunnel
sidebar_label: OctoPrint/Klipper Tunnel
---

## What is OctoPrint/Klipper Tunnel? {#what-is-octoprint-tunneling}

OctoPrint/Klipper Tunnel is a secure way to access the full OctoPrint/Klipper UI even when you are not on your home network

:::note
OctoPrint/Klipper Tunnel not available for private server users outside of their home network, unless the private server is set up to be accessible from the internet.
:::

## Is OctoPrint/Klipper Tunnel secure? {#is-octoprint-tunneling-secure}

It is as long as you:

- Don't share your Obico account with anyone.
- Make sure you only authorize the app that you trust to access the tunnel. If you are not sure, you can see [the list of all apps you have authorized here](https://app.obico.io/user_preferences/authorized_apps/) and remove the ones you no longer want.

Unlike port forwarding, your OctoPrint/Klipper is never exposed to the wild internet when you access it via the tunnel. Instead, your OctoPrint/Klipper page is loaded through 2 connections tunnelled together:

- The connection from OctoPrint/Klipper to the Obico server. The connection is authenticated using your account credential. So it's secure as long as you don't share your Obico account with anyone.
- The connection from your browser or your phone to the Obico server. This connection is authenticated using your account credential, or an access token if you have authorized any app to use the tunnel. Each app you authorized would receive their own access token.

Both connections are protected by end-to-end SSL encryption.

## How do I access OctoPrint/Klipper Tunnel? {#how-do-i-access-octoprint-tunneling}

Easy.

1. Make sure you have the latest version:

    - Obico for OctoPrint version **1.4.0 or higher**.
    - Obico for Klipper version **1.3.0 or higher**.

2. In the printer menu, select "OctoPrint Tunnel" or "Klipper Tunnel"

![](/img/user-guides/octoprint-tunnel.png)

## Is OctoPrint/Klipper Tunnel free to all users? {#is-octoprint-tunneling-free-to-all-users}

Yes and No. All users can use OctoPrint/Klipper Tunnel function. However, if you have a Free account, you are limited to tunnel up to 300MB per month. Once you have reached your monthly limit, you won't be able to tunnel to OctoPrint/Klipper any more until your usage is reset at the beginning of the next month.

The Pro plan subscribers get unlimited tunnel data.

## Why is monthly data cap limited to 300MB for a Free account? {#why-is-the-limit-on-free-account-only-100mb}

The reason why we can't give unlimited data to all accounts is because we need to temporarily store these data in our high-speed server cache, which is very expensive. In addition, any OctoPrint/Klipper data tunneled through the Obico Server has to be replicated 4 times. So 300MB data actually means we are charged for 1.2GB by our cloud provider!

Another reason for this limit is that every time OctoPrint/Klipper is being loaded via the tunnel, there is a big "spike" of server requests. Therefore, we have to "over-provision" Obico servers to be able to respond to these spikes if multiple users happen to be using OctoPrint/Klipper tunnel at the same time. Limiting the usage will help keep the server cost at a reasonable level while still providing a responsive experience anyone who wants to use OctoPrint/Klipper tunnel.

The good news is we have optimized how the tunnel works so that, for any file that has been downloaded to and cached in your browser, you won't need to download again. Therefore, although it'll cost a good chunk of your Free limit when you tunnel to your OctoPrint/Klipper for the first time, subsequent uses of the tunnel won't take nearly as much. Plus, the webcam streaming is not counted against this cap. For most people, 300MB is enough for you to tunnel to OctoPrint/Klipper for 3-6 hours. Assuming each time you spend 5 minutes in the tunnel, that's using the tunnel for 30-60 times, which should be good enough for most casual users in a month. If you need to tunnel to OctoPrint/Klipper frequently, your best option is to upgrade to the Obico Cloud Pro plan and enjoy unlimited tunnel data.

## Why does it take so long to load the OctoPrint/Klipper page in the Tunnel? {#why-does-it-take-so-long-to-load-the-octoprint-page-in-the-tunnel}

This is because, instead of directly loading into your browser, the OctoPrint/Klipper page has to travel a very long distance through the tunnel.

This is obviously different from other ways to directly access OctoPrint/Klipper, such as port forwarding, that may expose the traffic to malicious attackers. This is the cost we have to pay to make sure your OctoPrint/Klipper is protected from the potential security attacks.

The first time when you use OctoPrint/Klipper tunnel, it will be particularly slow because nothing is cached in your browser. However, subsequent uses should be a lot faster since most parts of the OctoPrint/Klipper page have already been cached.

Please [let us know](/docs/user-guides/contact-us-for-support) if OctoPrint/Klipper tunnel takes longer than 2 minutes to load on its first time, or longer than 30 seconds on the subsequent uses.

## It doesn't work for me! {#it-doesnt-work-for-me}

For some users, OctoPrint/Klipper may fail to load in the tunnel, or the tunnel page remains blank after 60 seconds:

![](/img/user-guides/octoprint_tunneling_blank_page.png)

This is usually caused by a slow internet connection on your Raspberry Pi.

However, all hopes are not lost even if you experience this problem. Please follow the steps below:

1. Refresh the tunnel page using your browser's refresh button. Please do NOT do a "hard-refresh". If you do not know what a "hard-refresh" is, then don't worry. You are not hard-refreshing.

2. Wait for 60 seconds to see if OctoPrint/Klipper will load this time.

3. If OctoPrint/Klipper still doesn't load, repeat steps 1 and 2 up to 5 times.

These steps will work for most users who couldn't get OctoPrint/Klipper to load in the tunnel on the first try. The reason why it works is, again, because OctoPrint/Klipper tunnel is optimized for reusing the cache in your browser. So when OctoPrint/Klipper fails to load on the first try and you refresh the page, the browser doesn't need to download the files that were already downloaded and cached in the browser.

## I got "Webcam stream not loaded" error in OctoPrint/Klipper! {#i-got-webcam-stream-not-loaded-error-in-octoprint}

We have disabled webcam feed in the OctoPrint/Klipper tunnel. The reason for that is OctoPrint/Klipper uses [M-JPEG](https://en.wikipedia.org/wiki/Motion_JPEG), a very inefficient streaming protocol that takes a lot of bandwidth. We simply can't afford to tunnel this volume of data via our servers.

We urge you to use [Obico's webcam feed](/docs/user-guides/webcam-streaming-for-human-eyes/) instead.
