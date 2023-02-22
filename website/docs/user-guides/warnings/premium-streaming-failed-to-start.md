---
id: premium-streaming-failed-to-start
title: Why do I get the "Premium webcam streaming failed to start" message?
---

[Premium webcam streaming](/docs/user-guides/webcam-streaming-for-human-eyes#1-premium-webcam-streaming) occasionally fails. When that happens, The Spaghetti Detective will automatically switch to [basic webcam streaming](/docs/user-guides/webcam-streaming-for-human-eyes#2-basic-webcam-streaming). At that moment, it'll display a warning in OctoPrint to keep you informed.

Premium webcam streaming may fail for a few reasons:

- Occasionally the Raspberry Pi or the webcam will decide that they want to take a break - just kidding. But if premium webcam streaming usually works for you, try to restart the Raspberry Pi to see if the problem will go away. Most of the times it will.
- Your webcam is a model that is not compatible with the "advanced streaming mode", and you have set the "compatibility mode" to "never". Check [this help doc](/docs/user-guides/streaming-compatibility-mode) to decide if you want to set the compatibility mode to "automatic" or "always".

Learn more abut [why premium webcam streaming is not working](/docs/user-guides/webcam-feed-is-laggy).
