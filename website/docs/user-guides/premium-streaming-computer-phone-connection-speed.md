---
id: premium-streaming-computer-phone-connection-speed
title: Test Phone/Computer's connection speed
---
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'


## Test if your phone/computer's Internet connection is fast enough for the Premium Streaming {#test-if-your-phonecomputers-internet-connection-is-fast-enough-for-the-premium-streaming}

If you are experiencing a choppy Premium Streaming, follow the instructions in this section to test if the Internet connection speed on your phone or computer is fast enough for the Premium Streaming.

If it is not, [here are a few options you have](#the-solutions-if-the-connection-speed-on-your-phonecomputer-is-not-fast-enough).

:::note
Even if the connection speed that your Internet/cellular provider promises you satisfies the [webcam streaming speed requirements](/docs/user-guides/internet-speed-requirement-premium-streaming/), it is possible there is a congested link along the connection chain from The Spaghetti Detective server to your phone.

Always follow the steps below to check the real connection speed you are getting.
:::

:::info
It's a lot more likely to have connection/bandwidth problems on a phone than on a computer.
:::

## If you are using a phone: {#if-you-are-using-a-phone}

When the webcam stream is choppy/jerky on a phone, the most common cause of it is the slow/unreliable Internet connection.

Not only are phones often connected to cellular networks with weak reception, but they are also likely more likely to have a lower connection speed than a computer even when the phone and the computer are connected to the same Wi-Fi router. This is because the Wi-Fi circuit in a phone is often weaker than the one in a laptop computer, and hence transmit weaker signals even if it's connected to the same Wi-Fi router as the computer.

There are a few ways to quickly test if the phone's connection speed is what is causing the webcam streaming problem.

### Switch phone's connection {#switch-phones-connection}

This is a quick but very effective way to test if the phone's connection is causing the streaming issue.

Switch your phone's connection and see if the problem goes away.

For instance, if your phone is currently connected to a Wi-Fi network, turn off Wi-Fi on your phone to force it to connect to a cellular network.  If your phone is currently connected to a cellular network but not Wi-Fi, find a Wi-Fi network and connect your phone to it.

After the switch, refresh The Spaghetti Detective streaming page if you are using the web app, or quit the app and restart it if you are using the mobile app.

If now you have a smooth webcam stream, it's confirmed that the phone's connection speed is the problem.

### Test the Premium Streaming on a computer {#test-the-premium-streaming-on-a-computer}

Open [The Spaghetti Detective web app](https://app.obico.io/) on a computer. If possible, try to run an Internet speed testing on the computer to make sure it has a solid connection.

If the webcam stream is smooth on the computer, it's confirmed that the phone's connection speed is the problem.

### Test your phone's Internet download speed with an app {#test-your-phones-internet-download-speed-with-an-app}

Run your favorite Internet speed testing app.

The number you need is the download speed in the test result. Compare this number to [the minimum Internet connection speed for Premium Streaming](/docs/user-guides/internet-speed-requirement-premium-streaming).

<Zoom overlayBgColorEnd="var(--ifm-background-surface-color)">
<img src="/img/user-guides/helpdocs/mobile-speed-test.jpg" style={{maxWidth: "308px"}} alt=""></img>
</Zoom>

You want to make sure the measured download speed is higher than the minimum speed with a comfortable margin. For instance, if the minimum speed is 10Mbps, you want to have at least 15Mbps download speed to be able to rule out the connection speed as the the problem.

## If you are using a computer {#if-you-are-using-a-computer}

Run your favorite Internet speed testing program.

The number you need is the download speed in the test result. Compare this number to [the minimum Internet connection speed for Premium Streaming](/docs/user-guides/internet-speed-requirement-premium-streaming).

<Zoom overlayBgColorEnd="var(--ifm-background-surface-color)">
<img src="/img/user-guides/helpdocs/computer-speed-test.png" style={{maxWidth: "308px"}} alt=""></img>
</Zoom>

You want to make sure the measured download speed is higher than the minimum speed with a comfortable margin. For instance, if the minimum speed is 10Mbps, you want to have at least 15Mbps download speed to be able to rule out the connection speed as the the problem.

## The solutions if the connection speed on your phone/computer is not fast enough {#the-solutions-if-the-connection-speed-on-your-phonecomputer-is-not-fast-enough}

You have 2 options here:

* Lower the webcam resolution or the streaming frame rate to match the connection speed on your phone/computer.
* Do nothing. Just put up with the problem. This may be a reasonable option if you don't often view the webcam stream on the device that has a low connection speed, and you don't want to sacrifice the resolution or the frame rate you can get on your other phones/computers.

:::info
Also check [test if the Raspberry Pi's Internet connection is fast enough for the Premium Streaming](/docs/user-guides/premium-streaming-raspberry-pi-connection-speed) if you are sure your phone/computer connection is fast enough.
:::