---
id: filament-change-notifications-with-octoprint
title: "Filament Runout and Color Change Notifications in OctoPrint and The Spaghetti Detective"

---

Filament runout sensors are great, but many users have reported that their filament runout sensors do not work properly when they are using OctoPrint. Luckily, the problem is not related to OctoPrint, it’s just a matter of enabling a few settings in your printer’s firmware that were likely disabled by the manufacturer. Follow along with this guide to get your filament runout sensor working with OctoPrint, and even get notified from The Spaghetti Detective through email or push notifications when your filament runs out or a color change is needed.



## Why Use A Filament Runout Sensor? {#why-use-a-filament-runout-sensor}

Without a filament runout sensor, using every last bit of filament is quite the challenge! If you test your luck and try to use up the last bit of a spool of filament, and you forget to swap to a new spool mid-print, you will end up printing a bunch of nothing! If you have a brittle filament and it snaps, your printer will end up air printing in a similar fashion. Filament runout sensors help you by stopping the print if either of the above happens.



These days, many 3D printers come with filament runout sensors. These sensors help you use up every last bit of filament without worrying about having a failed print because the filament runs out and the printer keeps printing. With a filament runout sensor, the printer is told to stop when the filament runs out or breaks so that you can change the filament and continue the print.



Since these sensors started getting popular, many users have reported that their filament sensors do not seem to be compatible with OctoPrint. Although the sensors are compatible, printer manufacturers often disable features necessary for the printer to communicate with OctoPrint in a friendly manner. Some printers ship with features disabled that make the filament sensor seem to not work at all when using OctoPrint. We want to fix that and we want OctoPrint and the 3D printer to be able to communicate better so OctoPrint can tell you when your filament has run out or alert you when it’s time to swap colors.



This guide will show you how to enable HOST_ACTION_COMMANDS and M600 in your Marlin 3D printer firmware so that OctoPrint can communicate with your 3D printer in a more friendly manner. Another command needed when using a filament runout sensor or when printing using pre-programmed filament color changes, is M600. If your printer came with a filament runout sensor, there is a good chance M600 is already enabled in your firmware, but we’ll check to make sure while we are at it.



## Enable HOST_ACTION_COMMANDS and M600 {#enable-host_action_commands-and-m600}

More likely than not, your printer was not shipped with HOST_ACTION_COMMANDS and/or M600 enabled. So you will need to recompile the firmware to get them enabled.

The process to recompile the firmware can vary slightly depending on what printer you have:

- If you have a Creality Ender 3 V2, or an Ender 3 V1 but have upgraded to a 32-bit mainboard such as SKR Mini E3, follow [this guide](/docs/user-guides/filament-change-notifications-with-octoprint-ender-3-v2).

- If you have a Prusa MINI/MINI+, follow [this guide](/docs/user-guides/filament-change-notifications-with-octoprint-prusa-mini).

If your printer is not listed above but has a 32-bit mainboard, follow [this general guide](/docs/user-guides/filament-change-notifications-with-octoprint-general-32bit). Once you figure out the process that is specific to your printer, please click "Edit this page" at the bottom of this guide to contribute it back to the community.


## Enabling Filament Change Notifications for OctoPrint and The Spaghetti Detective {#enabling-filament-change-notifications-for-octoprint-and-the-spaghetti-detective}

Now that you have updated your firmware, The Spaghetti Detective can notify you when a filament runout is detected or if a color change is prompted. If you don’t already have an account, sign up for free. The free plan allows unlimited printer notifications

You can turn on the filament notifications from the mobile app or the web app.

**Mobile App:**

<div style={{display: "flex", flexWrap: "wrap"}}>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/printer-screen.png" alt="Printer Screen"></img>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/preferences.png" alt="Select Preferences"></img>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/notification-screen.png" alt="Preferences Screen"></img>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/notifications.png" alt="Notifications Menu"></img>
</div>

1.  From the printer screen, click the three vertical lines on the upper left corner
2.  Select Preferences
3.  Select Notifications
4.  Select “Notify me when filament runs out or needs a change.” With this enabled, you will now be sent filament notifications to your email and through push notifications.
5.  You can enable filament runout and color change notifications to be sent through email or as a push notification to your phone.


**Enable Notifications**

<div style={{display: "flex", flexWrap: "wrap"}}>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/select-push-notifications.png" alt="Select Push Notifications"></img>
    <img style={{maxWidth: "220px", margin: "1em 0.5em 1em 0"}} src="/img/user-guides/filament-change/push-notification.png" alt="Push Notifications Screen"></img>
</div>

Select *Push Notification* from the *Notifications Screen*


**On The Spaghetti Detective's Website**

You can enable filament notifications from The Spaghetti Detective website too, but you can't change the push notification settings. Push notification settings can be changed in the mobile app as described above.

To enable filament change notifications from the website:

![Website Preferences](/img/user-guides/filament-change/preferences-website.jpg)
 1. From the printer screen, click *Preferences*.

 ![Website Preferences](/img/user-guides/filament-change/notifications-settings-website.jpg)

 2. Click *Notifications*
 3. Click "Notify me when filament runs out or needs a change."
