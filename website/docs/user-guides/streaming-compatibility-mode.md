---
id: streaming-compatibility-mode
title: Two modes in the Premium Streaming
sidebar_label: Two modes in the Premium Streaming
---

There are actually two different "modes" in the Premium Streaming:

* **Advanced mode**. This is the default mode.
* **Compatibility mode**.

As the name suggested, the advanced mode is superior to the compatibility mode in most cases. It is efficient in CPU usage, and hence able to stream at full speed - 25 frames per second However, not all webcams can be streamed in the advanced mode.

By default, the Obico plugin will try to stream in the advanced mode first. When it fails because of an incompatible webcam, it'll switch to the compatibility mode. So chances are you can leave the decision to Obico and she will figure out if the compatibility mode is right for you.

There are some rare situations when your webcam is compatible with the advanced mode, but the compatibility mode will suit your needs better. In these cases, you can tell Obi to "always stream in compatibility mode".

## The advanced mode vs the compatibility mode {#the-advanced-mode-vs-the-compatibility-mode}

Here is a comprehensive comparison between the compatibility mode and the advanced mode:

|  | Compatibility mode | Advanced mode |
|---|------|-------|
| **Webcam Compatibility** | Compatible with virtually any webcam or IP camera. | Compatible with [all Pi Cameras and most USB cameras](/docs/user-guides/25-fps-streaming-hw-compatibility). Not compatible with IP cameras. |
| **CPU usage** | High CPU usage. [May slow down 3D printer and cause print quality issues](#more-about-cpu-usage-in-compatibility-mode). | Low CPU usage. Rarely causes any print quality issues. |
| **Frame rate** | Any value specified in "*/boot/octopi.txt*". Has big impact on CPU usage. | Fixed at 25 frames per seconds. |
| **Resolution and aspect ratio** | Any value specified in "*/boot/octopi.txt*". Has big impact on CPU usage. | Limited options. |
| **Custom webcam settings** | All [custom webcam settings](https://community.octoprint.org/t/how-can-i-change-mjpg-streamer-parameters-on-octopi/203) in "*/boot/octopi.txt*" will be honored. | No custom webcam settings. "*/boot/octopi.txt*" is ignored. |

:::info
Learn more about [Webcam streaming resolution and frame rate](/docs/user-guides/webcam-streaming-resolution-framerate).
:::

## When should I "always stream in the compatibility mode"? {#when-should-i-always-stream-in-the-compatibility-mode}

:::caution
"Always streaming in compatibility mode" should be set with caution. It puts significantly more CPU load on the Raspberry Pi and may cause print quality issues if the resolution and/or frame rate is set too high.
:::

* You have a USB camera. And you are ok with streaming at a much lower frame rate in exchange for a webcam resolution higher than 640x480.
* You have configured multiple cameras for your OctoPrint. And the Obico plugin fails to use the correct one to stream from.
* You have custom webcam settings, auto-focus, white balance, etc., in either "*/boot/octopi.txt*" file or in Octolapse.
* The webcam is not connected to the Pi running OctoPrint. Examples include:
    * It is an IP camera.
    * It is a smartphone running an IP camera app.
    * The webcam is connected to another Pi.
    * Any other situations that require you to change the Snapshot URL settings in OctoPrint to be different than the default value of "*http://localhost:8080/?action=snapshot*" .
* You don't like the fact that [the webcam stream in OctoPrint now has a lower frame rate](/docs/user-guides/more-about-webcam-streaming/#now-i-have-the-awesome-25-fps-streaming-but-the-webcam-feed-in-octoprint-becomes-slower-why).

## How to change the compatibility mode setting? {#how-to-change-the-compatibility-mode-setting}

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
2. Scroll down the navigation bar on the left side.
3. Click "Obico for OctoPrint" tab.
4. Click the "Settings" button.

![](/img/user-guides/helpdocs/tsd-plugin-open-settings-page.gif)

5. In the "compatibility mode" section, change the setting to one that suits your needs.
6. Click the "Save" button.
7. **Restart the Raspberry Pi (very important).**


## More about CPU usage in compatibility mode {#more-about-cpu-usage-in-compatibility-mode}

The main downside of compatibility mode is it puts heavier loads on CPU than advanced mode does.

Whether or not this is a problem depends on what Pi you have, the resolution/frame rate configured for your webcam, and what kind of 3D models you are printing.

#### Check if compatibility mode is using too much CPU {#check-if-compatibility-mode-is-using-too-much-cpu}

If after switching to compatibility mode, your printer starts to stutter (brief pauses), and/or you start to have bumps on the print surface, high CPU usage may be the culprit.

![Bumps on the print surface](/img/user-guides/bumps_on_surface.png)

To confirm that, disable compatibility mode. If the problem goes away right after the compatibility mode is disabled, we know it is causing the problem.

#### Excessive CPU usage warning {#excessive-cpu-usage-warning}

Because of the potential problem caused by high CPU usage in compatibility mode, the Obico plugin monitors CPU usage and warns you when the streaming is using too much CPU. If that happens, take the following steps:

1. Lower the webcam resolution and frame rate in "*/boot/octopi.txt*".
2. Restart the Raspberry Pi.
3. Wait for 3 minutes.
4. If the warning shows up again, you should consider choosing "**Never stream in compatibility mode**".

## FAQs {#faqs}

#### Are there situations when I should "never stream in compatibility mode"? {#are-there-situations-when-i-should-never-stream-in-compatibility-mode}

The only situation where you may want to tell The Detective to "never stream in compatibility mode" is when it results in [excessive CPU usage and impacts the print quality](#more-about-cpu-usage-in-compatibility-mode).

**Don't forget to restart the Raspberry Pi after you change the setting to "never stream in compatibility mode".**

#### How can I adjust webcam resolution, frame rate, and other settings? {#how-can-i-adjust-webcam-resolution-frame-rate-and-other-settings}

It depends on which mode your webcam is streaming in. Learn more in [this guide](/docs/user-guides/webcam-streaming-resolution-framerate).

#### How can I find out if my webcam is currently streaming in the compatibility mode? {#how-can-i-find-out-if-my-webcam-is-currently-streaming-in-the-compatibility-mode}

Follow [this guide](/docs/user-guides/check-webcam-streaming-mode).