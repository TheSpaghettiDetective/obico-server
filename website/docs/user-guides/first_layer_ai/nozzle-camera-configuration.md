---
id: nozzle-camera-configuration
title: First Layer AI Configuration for Klipper Printers
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Required Hardware:
A nozzle camera that provides an up-close view of your 3D printers’ nozzle. 

### Recommended Cameras: 

- **[Mintion Nozzle Camera](https://www.mintion.net/products/mintion-nozzle-camera)**: 

- 3DO Nozzle Camera V1 or V2: 

   - 3DO Nozzle Camera Suppliers:
   - Kb3d
   - Fabreeko

## Compatible Printers

Obico’s first layer AI is compatible with any 3D printer running OctoPrint or Klipper, but there may not be a nozzle camera mount readily available for your 3D printer. Check with our nozzle camera partners, Mintion and 3DO to see if there is a mount for your printer. Of course, you can also check out various 3D model repositories such as Printables or Thingiverse, or you can design your own mount. 

## Configure Your Camera for First Layer AI

Obico now supports multiple webcam streams in the Obico app. You can configure your nozzle camera as a second camera in Obico, or you can just use the nozzle camera as your only camera. 

This guide assumes you have already configured either one or multiple webcams in fluidd or Mainsail. If you have not already configured one or multiple cameras in fluidd or Mainsail, you can follow our guide for Mainsail or the official crowsnest guide. 


<Tabs>
<TabItem value="nozzzle-camera-only" label="Configura Only A Nozzle Camera" default>

## Configure Obico to use only a nozzle camera

If you are setting up your nozzle camera as a secondary camera, select the "Multiple Cameras" tab instead.

Before proceeding, ensure your nozzle camera is plugged into your Raspberry Pi or 3D printer, and your nozzle camera is visible in fluidd/Mainsail and in Obico. 

<Tabs>
<TabItem value="mainsail" label="Mainsail" default>

### Mainsail
![](/img/user-guides/nozzle-cam-ai-config/mainsail-machine-tab.png)

1. Click “Machine” on the bottom left of the mainsail page
2. Click the “moonraker-obico.cfg” file to open it. 
3. Locate the section with [webcam].

4. Copy and paste the following line underneath the [webcam] section: 
``` is_nozzle_camera = True```

The section was: 

```
[webcam]
disable_video_streaming = False
```
It now becomes: 

```
[webcam]
disable_video_streaming = False
is_nozzle_camera = True
```

5. Click the Power Button in the top right corner of the screen and restart moonraker-obico for the changes to take effect in the Obico app.  
![](/img/user-guides/nozzle-cam-ai-config/mainsail-restart-moonraker-obico.gif)

</TabItem>
<TabItem value="fluidd" label="fluidd">


### Fluidd

![](/img/user-guides/nozzle-cam-ai-config/fluidd-configuration-tab.png)

1. Click “Configuration” on the left of the fluidd interface
2. Click the “moonraker-obico.cfg” file to open it. 
3. Locate the section with [webcam].
4. Copy and paste the following line underneath the [webcam] section: ``` is_nozzle_camera = True```

The section was: 

```
[webcam]
disable_video_streaming = False
```
It now becomes: 

```
[webcam]
disable_video_streaming = False
is_nozzle_camera = True
```
5. Click the three-dot Button in the top right corner of the screen and restart moonraker-obico for the changes to take effect in the Obico app.  

![](/img/user-guides/nozzle-cam-ai-config/fluidd-restart-moonraker-obico.gif)


</TabItem>
</Tabs>

</TabItem>
<TabItem value="multiple-cameras" label="Configure Multiple Cameras">

## Configure Obico to use multiple cameras 
<Tabs>
<TabItem value="mainsail" label="Mainsail">

### Mainsail

#### Step 1: Find the name of your webcam(s) in Mainsail

1. Open Mainsail 
2. Click the Gear icon on the top right of the page to open the “Settings” menu
3.Scroll down to “Webcams” 
![](/img/user-guides/nozzle-cam-ai-config/mainsail-webcam-settings.png)
4. Note the name of each of your webcams you want to add to Obico. In this example, we have one webcam named “C920” and another named “nozzle”. 

#### Step 2: Add Cameras to Obico Configuration

1. Click “Machine” on the bottom left of the mainsail page.
![](/img/user-guides/nozzle-cam-ai-config/mainsail-machine-tab.png)
2. Click the “moonraker-obico.cfg” file to open it. 
3. Locate the section with [webcam].
4. Configure the section so each camera is specified as a webcam followed by the name of the camera we found earlier. Add ```is_nozzle_camera = True``` to the camera that specifies your nozzle camera.  In this example, with one USB webcam called “C920” and one nozzle camera called “nozzle”, the webcam section was:

``` 
[webcam]
disable_video_streaming = False
``` 
It now becomes:

```
[webcam C920]
disable_video_streaming = False

[webcam nozzle]
disable_video_streaming = False
Is_nozzle_camera = True
``` 
:::warning
Webcam names are case sensitive! Be sure to match the case exactly as it appears in Mainsail
:::

:::note
The first [webcam] section will be your primary webcam. A primary webcam is what Obico uses for failure detection and generating timelapse videos.
For instance, if you have a minimum webcam section in moonraker-obico.cfg:
:::

5. Click “Save and close” to close the moonraker-obico configuration file. 
6. Click the Power Button in the top right corner of the screen and restart moonraker-obico for the changes to take effect in the Obico app.  
![](/img/user-guides/nozzle-cam-ai-config/mainsail-restart-moonraker-obico.gif)


</TabItem>
<TabItem value="fluidd" label="fluidd">

### Fluidd

#### Step 1: Find the name of your webcam(s) in Fluidd

1. Open Fluidd 
2. Click the Gear icon on the bottom left of the page to open the “Settings” menu.
![](/img/user-guides/nozzle-cam-ai-config/fluidd-webcam-settings.png)
3. Scroll down to “Cameras” 
4. Note the name of each of your webcams. In this example, we have one webcam named “C920” and another named “nozzle”. 

#### Step 2: Add Cameras to Obico Configuration

1. Click “Configuration” on the left of the fluidd interface.
![](/img/user-guides/nozzle-cam-ai-config/fluidd-configuration-tab.png)
2. Click the “moonraker-obico.cfg” file to open it. 
3. Locate the section with [webcam].
4. Configure the section so each camera is specified as a webcam followed by the name of the camera we found earlier. Add ```is_nozzle_camera = True``` to the camera that specifies your nozzle camera.  In this example, with one USB webcam called “c920” and one nozzle camera called “nozzle”, the webcam section goes from:

``` 
[webcam]
disable_video_streaming = False
``` 
It now becomes:

```
[webcam C920]
disable_video_streaming = False

[webcam nozzle]
disable_video_streaming = False
Is_nozzle_camera = True
``` 
:::warning
Webcam names are case sensitive! Be sure to match the case exactly as it appears in Mainsail
:::

:::note
The first [webcam] section will be your primary webcam. A primary webcam is what Obico uses for failure detection and generating timelapse videos.
For instance, if you have a minimum webcam section in moonraker-obico.cfg:
:::

5. Click “Save and close” to close the moonraker-obico configuration file. 
6. Click the three-dot Button in the top right corner of the screen and restart moonraker-obico for the changes to take effect in the Obico app.  
![](/img/user-guides/nozzle-cam-ai-config/fluidd-restart-moonraker-obico.gif)



</TabItem>
</Tabs>

## Check the stream in Obico
Now, you should see a new button on the webcam tab of the printer control page. Use it to swap back and forth between cameras or view multiple streams at once. 

![](/img/user-guides/nozzle-cam-ai-config/obico_multi-cam-interface-web.gif)

</TabItem>
</Tabs>


## Next Steps: Slicer Configuration

Once your camera is configured for first layer AI, [configure your slicer for first layer AI](http://localhost:3000/docs/user-guides/first_layer_ai/slicer-configuration-for-first-layer-ai-klipper-only/).

