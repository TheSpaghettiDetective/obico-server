---
title: Webcam streaming resolution and frame rate (Klipper)
---

:::danger
Raising resolution above 640x480 may cause potential issues:

- Excessive amount of CPU usage and [potentially print quality issues](webcam-streaming-excessive-cpu.md).
- The webcam stream [may be buffering](../webcam-feed-is-laggy/#buffering) a lot when the resolution is set too high. Raspberry Pi has a weak CPU so it can't handle the load of encoding high-resolution streams.

Most Raspberry Pi 4 users have reported they can set the resolution to 800x600 without any noticeable print quality or webcam streaming issues. Use caution when you go above 800x600.
:::

## Resolution {#resolution}

Obico for Klipper does webcam streaming at the same resolution as the configured webcam source configured in Mainsail/Fluidd.

When you change the resolution in the configured webcam source, Obico will change accordingly after the Raspberry Pi is rebooted.

## Framerate {#framerate}

The frame rate is up to 25FPS for the Premium Streaming, and up to 5FPS for the Basic Streaming. It is currently not configurable.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::
