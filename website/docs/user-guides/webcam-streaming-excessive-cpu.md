---
title: Excessive CPU usage on SBC board due to webcam streaming
sidebar_label: Excessive CPU usage
---

The bottle neck for streaming high resolution, high FPS video stream from your webcam is often the CPU on your SBC boards such as Raspberry Pi.

If you have set the resolution and FPS too high for your webcams, especially if you have set up to stream 2 webcams in Obico, the streaming process may cause excessive burden on your SBC's CPU. Not only will this cause the stream to fail to come through, but it may also cause printing quality problems.

## Check if compatibility mode is using too much CPU {#check-if-compatibility-mode-is-using-too-much-cpu}

If after increasing the webcam resolution and/or FPS in the webcam settings page, your printer starts to stutter (brief pauses), and/or you start to have bumps on the print surface, high CPU usage may be the culprit.

![Bumps on the print surface](/img/user-guides/bumps_on_surface.png)

To confirm that, [disable webcam streaming on the settings page](disable-25-fps-streaming.md). If the problem goes away right after the compatibility mode is disabled, we know it is causing the problem.

## How to fix it? {#how-to-fix-it}

Once confirmed that the excessive CPU usage is caused by the resolution/FPS being too high, what you can do is to experiment different levels of resolution and FPS until you find a sweet spot that you are happen with the streaming result, while not stressing your SBC so much that print quality is impacted.

If you have a Raspberry Pi 4 B/B+, you should be able to stream one webcam at high resolution at 25FPS, and a second webcam at medium resolution at 5FPS comfortably. Anything beyond this may start to cause problems.

If you have a Raspberry Pi 3 B/B+ or lower, you should be able to stream one webcam at medium resolution at 25FPS. If you want to stream two webcams, you will probably stream them at low resolution at 5-10FPS.


## How can I adjust webcam resolution, frame rate, and other settings? {#how-can-i-adjust-webcam-resolution-frame-rate-and-other-settings}

It depends on which mode your webcam is streaming in. Learn more in [this guide](/docs/user-guides/webcam-streaming-resolution-framerate).
