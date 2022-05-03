---
title: Project proposal - 3D printing problem detection using sound
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
tags: ['The Spaghetti Detective Updates']
---

The Detective has done a really good job at spotting, well, spaghetti for all of us! Kudos to her! However, there is only 1 problem: her hearing is no good. This small birth defect means:

- She can't detect anything that she can't see, such as the clicking sound when a step motor stalls.
- She can't detect anything that she can't see **clearly**. This means she usually needs to wait at least a few minutes for the spaghetti monster to fully reveal itself before she can catch it.

This is why we came up with a bold idea - if we fix The Detective's hearing, she will be able to catch the criminals earlier, or catch the ones she would otherwise miss!

<!--truncate-->

## Interesting! Tell me more.

The idea is simple. Most USB webcams come with a microphone these days (a silver lining of too many Zoom meetings at home). We can use these microphones to pick up the humming sound of your 3D printer, feed the sound data through an AI algorithm to determine, in real-time, if the printer is making sounds that are out of the ordinary.

If you have a webcam that doesn't come with a microphone, such as a Pi Camera, you can simply buy a USB microphone like [this](https://www.adafruit.com/product/3367?gclid=Cj0KCQjw9O6HBhCrARIsADx5qCRPxpILekRsMEV59vGaf7JBFdksWub_3DkgrB2tM5gQfl5Nr_ZbK-saArjYEALw_wcB).

We have done some preliminary research work to show, in a lab environment, this is an effective way to catch certain problems, typically the ones that are associated with distinctive sounds, such as a stalling step motor, a jammed nozzle, or a warped object that keeps on rubbing the tip of the nozzle.

## Great. But does it mean The Detective will eavesdrop on my house all the time? It sounds creepy!

We hear you. Having one Alexa in our house has made us uncomfortable enough. Nobody wants another one.

The good news is, the sound recording will never leave your house. As a matter of the fact, it won't even leave your Raspberry Pi.

There is a good chance that we can make the AI algorithm so simple that it can just directly run on the Raspberry Pi's CPU. Once the sound recording is picked up by your Raspberry Pi, it'll be crunched right there and immediately trashed afterward. Nobody can access the sound recording but yourself.

## What's the catch?

Every great thing comes with a catch. For this one, the catch is the amount of data required to train the AI algorithm. We need a lot of training data. I mean A LOT!

This is where you can pitch in to help. We need you to volunteers as a data contributor to collect sound samples from your 3D printer and submit them to us. We hope the TSD community members can work together to collect enough sound samples to train the world's first sound AI algorithm.

# Okay I'm in! How can I sign up as a data contributor?


Fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSfRmqLxlQseHDCkKqTkOYQF3Ara22I5LVlNrOhd8vS-XpecOA/viewform?usp=sf_link) to sign up as a data contributor.

As always, we will reward everyone who has helped us! We have yet to determine exactly how we will reward our data contributors because many things are still unknown (Is it going to be free? Do we need ongoing data collection? Will we ever have enough data?). But rest assured it'll be something that will make you feel good about the work you have done to help us! :)

### Let's work together to build the coolest AI project for 3D printing in 2021!