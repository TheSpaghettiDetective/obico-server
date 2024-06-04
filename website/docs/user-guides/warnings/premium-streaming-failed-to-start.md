---
id: premium-streaming-failed-to-start
title: Why do I get the "Premium webcam streaming failed to start" message?
---

[Premium webcam streaming](/docs/user-guides/webcam-streaming-for-human-eyes#1-premium-webcam-streaming) occasionally fails. When that happens, Obico will automatically switch to [basic webcam streaming](/docs/user-guides/webcam-streaming-for-human-eyes#2-basic-webcam-streaming). At that moment, it'll display a warning in OctoPrint to keep you informed.

Premium webcam streaming may fail for a few reasons:

- The SBC or 3D printer you are using doesn't have the `janus` system package required to create a WebRTC connection between your SBC and the Obico app. To fix it, make sure you have installed `janus` on your SBC. If your SBC is using a Debian-based OS, such as Raspberry Pi OS, you can SSH to the board and run `sudo apt-get install janus`.

- The SBC or 3D printer you are using doesn't have a hardware accelerator to encode H.264 stream using `ffmpeg`.

- Occasionally the Raspberry Pi or the webcam will decide that they want to take a break - just kidding. But if premium webcam streaming usually works for you, try to restart the Raspberry Pi to see if the problem will go away. Most of the times it will.

Learn more abut [why premium webcam streaming is not working](/docs/user-guides/webcam-feed-is-laggy).
