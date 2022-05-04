---
id: disable-25-fps-streaming
title: Should I disable the Premium Streaming? If so, how?
---

## Should I disable the Premium Streaming?

There are 2 reasons why you need to consider disabling the Premium Streaming:

1. **High CPU usage.** Streaming real video on Raspberry Pi's flimsy CPU is a tricky balancing act. It is possible in some situations The Detective tries too hard at her effort to send the best quality video streams to you. This may cause excessive CPU usage and hence impact the quality of your prints.

2. **Webcam streaming not working in OctoPrint.** If, after installing `Access Anywhere - The Spaghetti Detective` plugin, you can no longer see webcam stream in OctoPrint, you should restart the Raspberry Pi and wait for a few minutes to see if the webcam stream will appear. If not, you should consider disabling the premium webcam streaming.


## How can I do that?

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
2. Scroll down the navigation bar on the left side.
3. Click "Access Anywhere - The Spaghetti Detective" tab.
4. Click the "Settings" button.

![](/img/user-guides/helpdocs/tsd-plugin-open-settings-page.gif)

5. Check "Disable the Premium Webcam Streaming".
6. Click "Save".
7. Restart OctoPrint.

![Disable video streaming](/img/user-guides/settings-disable-25-fps-streaming.png)
