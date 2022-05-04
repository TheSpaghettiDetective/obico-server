---
id: detective-not-watching
title: Why is The Detective "not watching"?
sidebar_label: The Detective "not watching"?
---

If you open The Spaghetti Detective app and you see this warning, The Detective is not watching your prints for you. Hence you won't get alerted in case there is a print failure. 😟

![](/img/user-guides/helpdocs/not-watching.png)

Right below this warning, there is a short message that explains why The Detective decides not to watch your prints. Blow is a list of all possible reasons.

:::note
Whenever The Detective is not watching your prints, you are not using Detective Hours.
:::


#### 1. Your printer is not shown as "printing" in OctoPrint

The Detective relies on OctoPrint to know the status of your printer. Check OctoPrint to see if it shows your printer as "printing". If not, that's why The Detective is not watching. Figure out why OctoPrint doesn't pick up your printer status. The [OctoPrint online forum](https://community.octoprint.org/) is your friend here.

#### 2. You turned off "Watch for failures" option

There is a toggle right below the webcam feed box to let you easily turn on or off watching.

![Watch for failures is off](/img/user-guides/helpdocs/disable_watching.png)

:::tip
If you toggled of "**Watch for failures**" by accident, toggle it back on and The Detective will spring into action.
:::

#### 3. You told The Detective not to alert for this print

When you receive an alert, you have an option to turn off watching for current print only. This is very convenient when you have a print that is causing excessive amount of false alarms. Once the current print is over and the next print starts, The Detective will be back on the duty to watch prints for you.

#### 4. You have run out of AI Detection Hours

The Detective Hour balance for your account is displayed on the right hand side of the navigation bar. When it dips below 0, The Detective will stop watching your prints. There are [several ways to get more Detective Hours](/docs/user-guides/how-does-detective-hour-work#how-do-i-get-detective-hours).

![Watch for failures is off](/img/user-guides/helpdocs/negative-dh-balance.png)

