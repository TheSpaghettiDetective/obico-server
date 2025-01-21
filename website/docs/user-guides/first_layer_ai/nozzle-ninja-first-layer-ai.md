---
id: nozzle-ninja-first-layer-ai
title: Nozzle Ninja - First Layer AI
---


![](/img/user-guides/nozzle-cam-ai-config/what-is-first-layer-ai/nozzle_ninja_examples.png)


Since our early days as The Spaghetti Detective, Obico has been at the forefront of 3D print failure detection. Today, over a hundred thousand makers trust our technology which has caught [over one million failed 3D prints](https://obico.io/failure-detection.html)!

The Obico team is excited to announce our newest AI software, Nozzle Ninja - Obico's First Layer AI error detection system!


## Why Nozzle Ninja? {#why-nozzle-ninja}

Webcam based AI is great for detecting major 3D printing errors such as spaghetti, but it isn't as good at detecting less major flaws. Webcam based AI is also not great at detecting any issues with  the first layer of the print as the first layer is often blocked by the print head. The first layer is one of the most critical aspects of a 3D print, so we created Nozzle Ninja to help diagnose first layer issues including under-extrusion, over-extrusion, bed adhesion issues, warping, bubbling,nozzle blobbing and more! 



## What is a nozzle camera and why is it needed? {#what-is-a-nozzle-camera-and-why-is-it-needed}
A nozzle camera is a USB web camera that is specially designed to provide a very up close view of the 3D printer nozzle and the 3D print. While webcams are typically mounted in front of or on the 3D printer to provide a view of the whole 3D print bed, the nozzle camera provides a much narrower and zoomed in view. 

![](/img/user-guides/nozzle-cam-ai-config/what-is-first-layer-ai/nozzle_camera_versus_webcam.png)




## How does Nozzle Ninja work? {#how-does-nozzle-ninja-work}

Once configured, nozzle ninja will watch your prints during the first layer. At the end of the first layer, Obico will send you a report via:


**Print History**: First layer reports are included in the Print History section in the Obico web app and mobile app. Review your first layer and get suggestions about how to improve your print. Watch the Ai timelapse to see exactly what went wrong and when. 
![](/img/user-guides/nozzle-cam-ai-config/what-is-first-layer-ai/print_history_report_first_layer.png)



**Email**: Get a first layer report sent to your email. Each email includes a first layer grade (A-F) and An Ai timelapse so you can see exactly how the first layer was printer. 


**Push Notificaton**: Get a push notification with a snapshot of the first layer and a first layer grade so you know exactly how your print is doing no matter where you are. 


<img src="/img/user-guides/nozzle-cam-ai-config/what-is-first-layer-ai/push_notifications_first_layer_Ai.jpeg" 
     width="400" 
     height="500" />


## I’m in, How do I get started? {#im-in-how-do-i-get-started}

First, you’ll need a compatible nozzle camera:

- [Mintion Nozzle Camera](https://www.mintion.net/products/mintion-nozzle-camera)
- [3DO Nozzle Camera](https://3do.dk/3do-camera/2681-1913-3do-nozzle-camera-kit-v2-sony-4k-for-3d-printers.html)

Once you have a compatible camera, configure your nozzle camera for Nozzle Ninja first layer AI:

- [Nozzle Ninja First Layer Ai configuration for Klipper Printers](https://www.obico.io/docs/user-guides/first_layer_ai/nozzle-camera-configuration/)

- [Nozzle Ninja First Layer Ai configuration for OctoPrint Printers](https://www.obico.io/docs/user-guides/first_layer_ai/nozzle-camera-configuration-octoprint/)
