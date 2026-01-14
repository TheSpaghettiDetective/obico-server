---
id: failure-detection-false-alarms
title: Failure detection false alarms
sidebar_label: False alarms
---

Since The Detective has not been around the block for too long (For the record her birth certificate says February 12th, 2019. AND IT IS A GIRL!), she makes mistakes like all of us. To be fallible is to be human.

The Detective has openly admitted that the most common mistakes she makes are false alarms (but secretly she thinks it's just because she works too hard). Some examples:

![False alarm examples](/img/user-guides/false-alarm-examples.jpg)

## What do false alarms happen? {#what-do-false-alarms-happen}

Behind the scene The Spaghetti Detective is leveraging AI technology to detect print failures. Specifically, it is a Deep Learning algorithm that is trained to look for patterns of spaghetti shape. This technology is not much different from the ones used in Apple's Face ID, Amazon Alexa, or self-driving cars. Deep Learning is still a fast-developing technology that is far from being perfect. If you own one of these products you probably know what I mean.

Also, since we have not worked on The Spaghetti Detective for too long, we have not collected enough data to train the Deep Learning algorithm. We are still trying to figure out how we can have a way to gather more training data while not invading user's privacy. As the result of not having much training data, The Detective is making more mistakes than we'd like her to.

## What are the common false alarms? {#what-are-the-common-false-alarms}

Our users have reported quite a few things The Detective is likely to get wrong, including:

- Bed clips.
- Flower vase.
- Extruder's reflection on the glass bed.
- [The beautiful logo on Ender 3's bed](https://i.all3dp.com/wp-content/uploads/2019/01/24120918/Ender_3_Plate.jpg) or other text.
- [Scraps of previously-failed prints hidden under the bed](https://twitter.com/LukesLaboratory/status/1108591412386385925). Well this one is technically not a false alarm but still...

## What can I do to minimize the chance of false alarms? {#what-can-i-do-to-minimize-the-chance-of-false-alarms}

Fortunately a few simple measures can be taken to avoid most of the false alarms. This is particularly important before The Detective has the time and resource needed to be trained into Sherlock Holmes.

- [Review the time-lapses](https://app.obico.io/prints/) from time to time to see what objects confuse The Detective the most, and, if possible, move them to a different place so that they are not in the camera's view.
- If it's not practical to remove the objects that cause confusion, e.g., the extruder's reflection on the glass bed, you can adjust the angle and position of the camera to see if it helps.
- If you are still getting excessive false alarms, you can adjust [the alertness level](/docs/user-guides/detection-print-job-settings/#how-alerted-do-you-want-the-detective-to-be-on-this-printer) in printer settings to low.
- If setting the alertness level still doesn't help, you can change the printer settings so that The Detective won't pause the print on false alarm ([here is how](/docs/user-guides/detection-print-job-settings/#when-potential-failure-is-detected)). The Detective is quite adaptive. Once she realizes she is detecting certain patterns over and over again in all prints, she will realize that she must be wrong with it and correct herself.

## Any other things I can do? {#any-other-things-i-can-do}

You can check your camera setup to see if it's optimal. It not only helps The Detective improve the detection rate, but also provides a better viewing experience for human's eyes.

- Whenever possible, avoid backlight. A simple rule of thumb is to have the light source and camera co-located closely together on the same side of the printer.
- If your webcam comes with an adjustable lens, adjust its focal length so that it's focused on the printing area.
- Position your webcam so that the printing area largely fills the whole camera view.
