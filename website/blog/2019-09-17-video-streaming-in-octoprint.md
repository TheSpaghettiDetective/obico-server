---
title: Video Streaming Is Here!
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.obico.io/img/kj.jpg
tags: ['OctoPrint', 'Webcam Streaming']
---

We get it. Even if you have The Detective on the watch for you, you won't have a complete peace of mind until you see the webcam feed with your own eyes. That's why we just built the video feed and it's now in alpha testing. You can earn DG credits by enrolling in the alpha testing and reporting bugs to us!

<!--truncate-->

## The requirements to enroll in video streaming alpha testing

Video streaming is still in active development, and it is using WebRTC, a technology not fully supported on all platforms. So please check the follow items to make sure you have what's needed to enroll in alpha testing.

* Raspberry Pi 3B/3B+, or Zero/Zero W. It won't work if your OctoPrint is running on a PC. It may work with Raspberry Pi 2 or earlier version but we haven't tested it on them yet.

* Pi Camera module. Currently video streaming only works with Pi Camera [such as this one](https://www.raspberrypi.org/products/camera-module-v2/). USB cameras will be supported later. Stay tuned for our updates on when we add the support.

*Special note: If you have an OctoPrint Anywhere PRO/PRO+ account, you can't enroll in alpha testing. This is because both OctoPrint Anywhere PRO/PRO+ streaming and TSD streaming needs to have access to Pi Camera hardware, and Pi Camera doesn't allow shared access. But hey - you already have the better 25 FPS streaming with OctoPrint Anywhere PRO/PRO+ anyway. :)*

## Browser compatibility

Again, because WebRTC is a new technology, it's not yet well supported by all browsers and Operating Systems. But we expect it to gain wider support in the next few years. For now:


* iPhone with iOS 11+. If you have an iPhone, you are in luck as the support for WebRTC is solid. The video streaming works on any iPhone or iPad that can be upgraded to iOS 11 or above.

* Android phones... The support of WebRTC on Android devices is a lot more complicated. Here is the rule of thumb:
    * Phones that run Android 9+: YES.
    * Phones that run Android 8.x: Maybe. You can try it to see if it works.
    * Phones that can't be upgraded to Android 8.0. No. :(

* On computer, it currently only works in FireFox. This is due to a tricky bug in our software rather than WebRTC compatibility. This bug is on our radar but we probably won't get around to it very soon since most of our users watch webcam feed on a phone, not on a computer.


## To enroll in video streaming alpha testing

1. Upgrade The Spaghetti Detective plugin to version 0.8.0 when OctoPrint prompt you to do so.

2. Turn on video streaming by going to OctoPrint settings --> The Spaghetti Detective (beta) --> Opt In --> Smooth video streaming testing.

![Opt in alpha testing](/img/blogs/video-streaming-alpha-testing.png)

3. Restart OctoPrint. Video streaming won't come in until you restart OctoPrint.

## Give us feedback. Report bugs. Earn DG credits!

Please help us test video streaming and give us feedback on how it works for you. Or report bugs if you run into any.

* Send email to [support@thespaghettidetective.com](mailto:support@thespaghettidetective.com) to give us feedback or report bugs.

* For any feedback to give us, even if it's just a line "hey it works!", or "no it sucks. it doesn't work for me!", we will reward you with 50 DG credits.

* When you report a bug, we will work with you to reproduce it. Once we are able to reproduce it, you will be rewarded with 200 DG credits even if the same bug has been reported by other users.
