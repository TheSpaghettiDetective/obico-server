---
id: connectivity-error-report
title: Use the diagnostic page to help with troubleshooting
---

Obico for OctoPrint plugin provides an advanced diagnostic page that can help you understand the severity of the connection issue that happen under the hood so that you can make informed decision if/how you should fix it.

## Understand the Diagnostic Report {#understand-the-diagnostic-report}

The Diagnostic Report may looks like this:

![](/img/user-guides/helpdocs/diagnostic-report.png)

Depending on whether or not there have been errors, there may be up to 2 parts in the report:

1. This part displays the issues related to the connection to the Obico Server. This part will be missing if there have been no server connection errors since the restart of OctoPrint.
1. This part displays the issues related to the connection to your webcam. This part will be missing if there have been no webcam errors since the restart of OctoPrint.

## How to assess the server connectivity issues {#how-to-assess-the-server-connectivity-issues}

The info you need to assess the server connectivity issues is highlighted in this screenshot.

![](/img/user-guides/helpdocs/tsd-plugin-diagnostic-page-server-connection.png)

#### Error rate {#error-rate}

When the error rate is smaller than 5%, it is usually not a problem as you can still use Obico mobile app or web app just fine, often without even noticing even the slightest glitches.

However, if the error rate is higher than 20%, you may want to take action to figure out what is wrong.

#### Occurrence of the first error and the most recent error {#occurrence-of-the-first-error-and-the-most-recent-error}

The timestamp when the first error and the most recent error happened, respectively.

From these diagnostic information, you can determine:

1. How often do server connection problems happen?
2. Do the problems happen in bursts, or randomly throughout the time?
3. Are the problems still actively happening. If so, this probably explain whatever issues you are experiencing.

:::note
Please note only the errors happened in the current OctoPrint session. Errors from all the previous OctoPrint sessions are erased.
:::

### 4.1 If the error rate is 100%: {#41-if-the-error-rate-is-100}

This means your OctoPrint has no connection to the server at all.

The problem is most likely networking-related, such as ill-configured Wi-Fi dongle, DNS configuration error, routing problem, restrictive firewall rules, etc.

Troubleshooting networking issues is outside the scope of this guide. But a good start is probably to run a "curl" command on the system on which the OctoPrint runs.

For instance, if you run OctoPrint on a Raspberry Pi, just like 90% of other OctoPrint users, the commands will be:

1. SSH to the Raspberry Pi.
1. Once you are on the Pi, run `curl https://app.obico.io/`. If the Pi has a good connection to the Obico Server, the command won't report any error.

:::note
If you are not running the OctoPrint on a Raspberry Pi, the commands may be slightly different.
:::

The error you may see will probably be very hard to understand. Remember you can always [get help from a human](/docs/user-guides/contact-us-for-support).

### 4.2 If the error rate is less than 100%: {#42-if-the-error-rate-is-less-than-100}

This means your OctoPrint has intermittent connection problems to the server.

A comprehensive list for fixing intermittent Internet connection problems is outside the scope of this guide. But based on what we have learned from tens of thousands of OctoPrint users, Wi-Fi signal strength accounts for 90% of the connection problems. This is especially true on Raspberry Pis as they have a very weak Wi-Fi circuit.

Below is a list of some quick things you can do to confirm a Wi-Fi problem and fix it.

* If there is an option, use an ethernet cable to connect the Raspberry Pi to the router.
* If you are using an ethernet cable, you should choose Category 5e or higher, preferably Category 6a or Category 7.
* If ethernet cable is not an option, move the Raspberry Pi as close to the router as possible.
* If you can move your router to be closer to the Raspberry Pi, do it too. Remember, distance is the No. 1 killer when it comes to Wi-Fi signal strength.
* If it's not an option to relocate the Pi or the router to be closer to each other, Wi-Fi repeater is another option. You may want to temporarily move the Pi close to the router just to make sure the Wi-Fi signal strength is the cause of the problem because you shell out some $$$ for a Wi-Fi repeater.


## How to assess the webcam connectivity issues {#how-to-assess-the-webcam-connectivity-issues}

In most case, your webcam is connected to the Raspberry Pi, or is on the same WiFi network. So it should rarely fail. If you are seeing any errors here, it's most likely caused by the misconfigured webcam settings in OctoPrint.

Follow [these steps](/docs/user-guides/webcam-feed-is-not-showing#the-webcam-streaming-in-octoprint-has-problems) to figure out the configuration problem and fix it.