---
id: detective-not-watching
title: Why is the Failure Detection Off?
sidebar_label: Why is the Failure Detection Off?
---

If you open the Obico app and you see this warning, the failure detection is off for your prints. Hence you won't get alerted in case there is a print failure. 😟

![](/img/user-guides/helpdocs/not-watching.png)

Right below this warning, there is a short message that explains why the failure detection is off. Below is a list of all possible reasons.

:::note
Whenever the failure detection is off, you are not using AI Detection Hours.
:::


#### 1. Your printer is not actively printing {#1-your-printer-is-not-actively-printing}

Obico relies on OctoPrint to know the status of your printer. Check OctoPrint to see if it shows your printer as "printing". If not, that's why the failure detection is off. Figure out why OctoPrint doesn't pick up your printer status. The [OctoPrint online forum](https://community.octoprint.org/) is your friend here.

#### 2. You have disabled the "AI failure detection" option {#2-you-have-disabled-the-ai-failure-detection-option}

There is a toggle right below the webcam feed box to let you easily turn on or off failure detection.

![Enable AI failure detection ](/img/user-guides/helpdocs/disable_watching.png)

#### 3. You told The Detective not to alert for this print {#3-you-told-the-detective-not-to-alert-for-this-print}

When you receive an alert, you have an option to turn off failure detection for current print only. This is very convenient when you have a print that is causing excessive amount of false alarms. Once the current print is over and the next print starts, The Detective will be back on the duty to watch prints for you.

#### 4. You have run out of AI Detection Hours {#4-you-have-run-out-of-ai-detection-hours}

The AI Detection Hour balance for your account is displayed on the right hand side of the navigation bar. When it dips below 0, failure detection will be paused for your prints. There are [several ways to get more AI Detection Hours](/docs/user-guides/how-does-detective-hour-work#how-do-i-get-detective-hours).

![](/img/user-guides/helpdocs/negative-dh-balance.png)

[](#2-you-have-disabled-the-"ai-failure-detection"-option)
