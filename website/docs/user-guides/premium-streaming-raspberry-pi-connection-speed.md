---
id: premium-streaming-raspberry-pi-connection-speed
title: Test Raspberry Pi's connection speed
---
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'

## Test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming {#test-if-the-raspberry-pis-internet-connection-is-fast-enough-for-the-premium-streaming}

The Raspberry Pi needs to have fast and reliable Internet **upload speed** to be able to shovel all the video frames to your phone/computer without dropping too many of them.

If you are experiencing a choppy Premium Streaming, follow the instructions in this section to test if the Internet connection speed on your phone or computer is fast enough for the Premium Streaming.

If it is not, [here are a few options you have](#the-solutions-if-the-connection-speed-on-your-raspberry-pi-is-not-fast-enough).

:::note
Even if the connection speed that your Internet/cellular provider promises you satisfies the [webcam streaming speed requirements](/docs/user-guides/internet-speed-requirement-premium-streaming/), it is possible there is a congested link along the connection chain from The Spaghetti Detective server to your Raspberry Pi.

Always follow the steps below to check the real connection speed you are getting.
:::

:::note
Dropping a few video frames occasionally is fine. You may not even notice it in The Spaghetti Detective Premium Streaming. However, if the stream will become choppy/jerky if more than 10% of the frames are dropped.
:::

## If your Raspberry Pi is connected to Wi-Fi {#if-your-raspberry-pi-is-connected-to-wi-fi}

More likely than not, when the Premium Stream is choppy or jerky, it's because the Raspberry Pi doesn't have a fast/reliable enough Wi-Fi connection.

An Internet connection over Wi-Fi is subject to many factors ranging from the distance to the router to the number of devices fighting for the limited bandwidth. The weak built-in Wi-Fi circuit in the Raspberry Pi certainly exacerbates the problem.

Try the following things to test if the Wi-Fi connection is responsible for your webcam streaming problem:

* If there is an option, [use an ethernet cable to connect the Raspberry Pi to the router](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/using-a-wired-network).
* Move the Raspberry Pi as close to the router as possible. You don't have to find a perfect spot for the Pi as this move is temporary while you are testing the connection.
* If you can move your router to be closer to the Raspberry Pi, do it too. Remember, distance is the No. 1 killer when it comes to Wi-Fi signal strength.
* If you have a [Wi-Fi repeater (aka Wi-Fi booster, Wi-Fi extender)](https://www.waveform.com/pages/wifi-booster-repeater-extender-differences) handy, use it.

If the webcam streaming becomes smooth after you take any one of the steps above, the Wi-Fi connection of your Raspberry Pi is not good enough for the Premium Streaming. You have [a few options to implement a permanent solution](#the-solutions-if-the-connection-speed-on-your-raspberry-pi-is-not-fast-enough).

If, however, the streaming problem persists even after you have tried as many of these measures as possible, you can [directly test the upload speed of the Raspberry Pi's Wi-Fi connection](#test-upload-speed-on-the-raspberry-pi).

## If your Raspberry Pi is connected to Ethernet cable {#if-your-raspberry-pi-is-connected-to-ethernet-cable}

If you are using an Ethernet cable that is Category 5 or below, and there is an option, replace it with a Category 5e or higher, preferably Category 6a or Category 7.

If you don't have an Ethernet cable of higher categories, or changing to it doesn't solve the streaming problem, you can [directly test the upload speed of the Raspberry Pi's Wi-Fi connection](#test-upload-speed-on-the-raspberry-pi).

## Test upload speed on the Raspberry Pi {#test-upload-speed-on-the-raspberry-pi}

:::caution
Testing upload speed in the Raspberry Pi requires technical skills such as SSH and shell (Bash) commands.
:::

1. [Log into the Raspberry Pi via SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/).

2. Once you are in the Raspberry Pi, run the follow commands:

```bash
source /home/pi/oprint/bin/activate
pip install speedtest-cli
speedtest-cli
```

<Zoom overlayBgColorEnd="var(--ifm-background-surface-color)">
<img src="/img/user-guides/helpdocs/speed-test-raspberry-pi.gif" style={{maxWidth: "308px"}} alt=""></img>
</Zoom>

3. Get the upload speed from the test result. In this example, the upload speed is 5.9Mbps. Compare this number to [the minimum Internet connection speed for Premium Streaming](/docs/user-guides/internet-speed-requirement-premium-streaming).

You want to make sure the measured upload speed is higher than the minimum speed with a comfortable margin. For instance, if the minimum speed is 10Mbps, you want to have at least 15Mbps download speed to be able to rule out the connection speed as the the problem.


## The solutions if the connection speed on your Raspberry Pi is not fast enough {#the-solutions-if-the-connection-speed-on-your-raspberry-pi-is-not-fast-enough}

This won't be a comprehensive list for fixing Internet connection problems for your Raspberry Pi, as they are outside the scope of this guide.

Based on what we have learned from tens of thousands of OctoPrint users, Wi-Fi signal strength accounts for 90% of the connection problems. This is because the Raspberry Pi has a very weak Wi-Fi circuit.

Below is a list of some quick things you can do to confirm a Wi-Fi problem and fix it.

* If there is an option, [use an ethernet cable to connect the Raspberry Pi to the router](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/using-a-wired-network).
* If you are using an ethernet cable, you should choose Category 5e or higher, preferably Category 6a or Category 7.
* If ethernet cable is not an option, move the Raspberry Pi as close to the router as possible.
* If you can move your router to be closer to the Raspberry Pi, do it too. Remember, distance is the No. 1 killer when it comes to Wi-Fi signal strength.
* If it's not an option to relocate the Pi or the router to be closer to each other, Wi-Fi repeater is another option. You may want to temporarily move the Pi close to the router just to make sure the Wi-Fi signal strength is the cause of the problem because you shell out some $$$ for a Wi-Fi repeater.

:::note
These tips are primarily for the Raspberry Pi, which is what most users use to run OctoPrint. However, the same principles should apply if you are running OctoPrint on other platforms such as a PC.
:::


:::info
Also check [test if your phone/computer's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-computer-phone-connection-speed) if you are sure your Raspberry Pi's connection is fast enough.
:::
