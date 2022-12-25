---
id: octoprint-tunneling
title: OctoPrint Tunneling
sidebar_label: OctoPrint Tunneling
---

## What is OctoPrint Tunneling? {#what-is-octoprint-tunneling}

OctoPrint Tunneling is a secure way to access the full OctoPrint UI even when you are not on your home network

:::note
OctoPrint Tunneling not available for private server users outside of their home network, unless the private server is set up to be accessible from the internet.
:::

## Is OctoPrint Tunneling secure? {#is-octoprint-tunneling-secure}

It is as long as you:

* Don't share your Obico account with anyone.
* Make sure you only authorize the app that you trust to access the tunnel. If you are not sure, you can see [the list of all apps you have authorized here](https://app.obico.io/user_preferences/authorized_apps/) and remove the ones you no longer want.

Unlike port forwarding, your OctoPrint is never exposed to the wild internet when you access it via the tunnel. Instead, your OctoPrint page is loaded through 2 connections tunnelled together:

* The connection from OctoPrint to the Obico server. The connection is authenticated using your account credential. So it's secure as long as you don't share your Obico account with anyone.
* The connection from your browser or your phone to the Obico server. This connection is authenticated using your account credential, or an access token if you have authorized any app to use the tunnel. Each app you authorized would receive their own access token.

Both connections are protected by end-to-end SSL encryption.

## How do I access OctoPrint Tunneling? {#how-do-i-access-octoprint-tunneling}

Easy.

1. Make sure you have upgraded the plugin to version **1.4.0 or higher**.

2. In the printer menu, select "Tunneling".

![](/img/user-guides/octoprint-tunnel.png)

## Is OctoPrint Tunneling free to all users? {#is-octoprint-tunneling-free-to-all-users}

Yes and No. All users can use OctoPrint Tunneling function. However, if you have a Free account, you are limited to tunneling up to 300MB per month. Once you have reached your monthly limit, you won't be able to tunnel to OctoPrint any more until your usage is reset at the beginning of the next month.

The Pro plan subscribers get unlimited tunneling.

## Why is monthly data cap limited to 300MB for a Free account? {#why-is-the-limit-on-free-account-only-100mb}

The reason why we can't give unlimited data to all accounts is because we need to temporarily store these data in our high-speed server cache, which is very expensive. In addition, any OctoPrint data tunneled through the Obico Server has to be replicated 4 times. So 300MB data actually means we are charged for 2GB by our cloud provider!

Another reason for this limit is that every time OctoPrint is being loaded via the tunnel, there is a big "spike" of server requests. Therefore, we have to "over-provision" Obico servers to be able to respond to these spikes if multiple users happen to be using OctoPrint Tunneling at the same time. Limiting the usage will help keep the server cost at a reasonable level while still providing a responsive experience anyone who wants to use OctoPrint Tunneling.

The good news is we have optimized our tunneling so that, for any file that has been downloaded to and cached in your browser, you won't need to download again. Therefore, although it'll cost a good chunk of your Free limit when you tunnel to your OctoPrint for the first time, subsequent uses of the tunneling won't take nearly as much. Plus, the webcam streaming is not counted against this cap. For most people, 300MB is enough for tunneling to OctoPrint for 5-10 hours. Assuming each time you spend 5 minutes in the tunnel, that's using the tunnel for 60-120 times, which should be good enough for most casual users in a month. If you need to tunnel to OctoPrint frequently, your best option is to upgrade to the Obico Cloud Pro plan and enjoy unlimited tunneling.

## Why does it take so long to load the OctoPrint page in the Tunnel? {#why-does-it-take-so-long-to-load-the-octoprint-page-in-the-tunnel}

This is because, instead of directly loading into your browser, the OctoPrint page has to travel a very long distance through the tunnel.

This is obviously different from other ways to directly access OctoPrint, such as port forwarding, that may expose the traffic to malicious attackers. This is the cost we have to pay to make sure your OctoPrint is protected from the potential security attacks.

The first time when you use OctoPrint Tunneling, it will be particularly slow because nothing is cached in your browser. However, subsequent uses should be a lot faster since most parts of the OctoPrint page have already been cached.

Please [let us know](/docs/user-guides/contact-us-for-support) if OctoPrint Tunneling takes longer than 2 minutes to load on its first time, or longer than 30 seconds on the subsequent uses.

## It doesn't work for me! {#it-doesnt-work-for-me}

For some users, OctoPrint may fail to load in the tunnel, or the tunnel page remains blank after 60 seconds:

![](/img/user-guides/octoprint_tunneling_blank_page.png)

This is usually caused by a slow internet connection on your Raspberry Pi.

However, all hopes are not lost even if you experience this problem. Please follow the steps below:

1. Refresh the tunneling page using your browser's refresh button. Please do NOT do a "hard-refresh". If you do not know what a "hard-refresh" is, then don't worry. You are not hard-refreshing.

2. Wait for 60 seconds to see if OctoPrint will load this time.

3. If OctoPrint still doesn't load, repeat steps 1 and 2 up to 5 times.

These steps will work for most users who couldn't get OctoPrint to load in the tunnel on the first try. The reason why it works is, again, because OctoPrint Tunneling is optimized for reusing the cache in your browser. So when OctoPrint fails to load on the first try and you refresh the page, the browser doesn't need to download the files that were already downloaded and cached in the browser.

## I got "Webcam stream not loaded" error in OctoPrint! {#i-got-webcam-stream-not-loaded-error-in-octoprint}

We have disabled tunneling webcam feed in OctoPrint. The reason for that is OctoPrint uses [M-JPEG](https://en.wikipedia.org/wiki/Motion_JPEG), a very inefficient streaming protocol that takes a lot of bandwidth. We simply can't afford to tunnel this volume of data via our servers.

We urge you to use [Obico's webcam feed](/docs/user-guides/webcam-streaming-for-human-eyes/) instead.
