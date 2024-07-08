---
id: nozzle-camera-configuration-octoprint
title: First Layer AI Configuration for OctoPrint Printers
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';



## Required Hardware: {#required-hardware}
A nozzle camera that provides an up-close view of your 3D printers’ nozzle.

A nozzle camera is a specialized web camera. Nozzle cameras are much smaller than traditional webcams allowing them to get an up-close view of the 3D printer nozzle and the print. With a nozzle camera configured with your 3D printer, you can enable Nozzle Ninja, Obico's first layer AI, to watch your first layer for various types of print issues including over-extrusion, under-extrusion, poor bed adhesion and more. 

### Recommended Cameras {#recommended-cameras}

- **[Mintion Nozzle Camera](https://www.mintion.net/products/mintion-nozzle-camera)**: 

- **[3DO Nozzle Camera V1 or V2](https://3do.eu/59-3do-camera)**: 

   - 3DO Nozzle Camera Suppliers:
   - Kb3d
   - Fabreeko

## Compatible Printers {#compatible-printers}

Obico’s first layer AI is compatible with any 3D printer running OctoPrint or Klipper, but there may not be a nozzle camera mount readily available for your 3D printer. Check with our nozzle camera partners, Mintion and 3DO to see if there is a mount for your printer. Of course, you can also check out various 3D model repositories such as Printables or Thingiverse, or you can design your own mount. 



:::tip
Prefer watching a video instead? The video below walks through the process of configuring a standard USB webcam with a nozzle camera. It also goes through the process of adding multiple webcams to OctoPrint in case you haven't done that already (cameras must be configured in Mainsail/fluidd before adding them to Obico).
:::

<div className="videoWrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/BFV9HgJkRJI?si=wRyuRxZ2ypMZOVVD" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## Configure Your Camera for First Layer AI {#configure-your-camera-for-first-layer-ai}

Obico now supports multiple webcam streams in the Obico app. You can configure your nozzle camera as a second camera in Obico, or you can just use the nozzle camera as your only camera. 

<Tabs>
<TabItem value="nozzzle-camera-only" label="Configure Only One Nozzle Camera" default>

![](/img/user-guides/nozzle-cam-ai-config/octoprint/octoprint-1-webcam.png)

If you are setting up your nozzle camera as a secondary camera, select the "Multiple Cameras" tab instead.

Before proceeding, ensure your nozzle camera is plugged into your Raspberry Pi or 3D printer, and your nozzle camera is visible in OctoPrint and in Obico. Also, ensure Obico for Octoprint is updated to Obico for OctoPrint version 1.6.8 or newer. 

1. Open the OctoPrint interface.
2. Click the wrench icon on the top right of the screen to open the OctoPrint Settings menu.
3. Scroll down to "Obico for OctoPrint" 
4. Click "Settings" 
![](/img/user-guides/nozzle-cam-ai-config/octoprint/octoprint-obico-webcam-settings-single.png)

1. Under "Primary Camera", select your camera from the dropdown menu. Skip "Secondary Camera" since you are only setting up one camera.
2. Under "Nozzle Camera", select your camera from the dropdown menu. 
3. 8. Click "Save" to save the settings.
4. Click the "Power" icon in the top right of the screen. Restart OctoPrint for the changes to take effect. 


</TabItem>
<TabItem value="multiple-cameras" label="Configure Multiple Cameras">

![](/img/user-guides/nozzle-cam-ai-config/octoprint/octoprint-1-webcam.png)

1. Open the OctoPrint interface.
2. Click the wrench icon on the top right of the screen to open the OctoPrint Settings menu.
3. Scroll down and click "Obico for OctoPrint" 
4. Click "Settings" 
![](/img/user-guides/nozzle-cam-ai-config/octoprint/octoprint-obico-webcam-settings-multi.png)

5. Under "Primary Camera", select a primary camera. The primary camera will be used for standard webcam-based AI failure detection. 
6. Under "Secondary Camera", select a secondary camera. We recommend selecting your nozzle camera as the secondary camera. 
7. Under "Nozzle Camera", select your nozzle camera from the dropdown menu. 
8. Click "Save" to save the settings.
9. Click the "Power" icon in the top right of the screen. Restart OctoPrint for the changes to take effect. 


</TabItem>
</Tabs>