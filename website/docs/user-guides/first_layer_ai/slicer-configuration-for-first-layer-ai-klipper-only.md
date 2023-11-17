---
title: First Layer AI Slicer Configuration for Layer Scan (For Klipper Users)
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::warning
Slicer configuration is only required for Klipper. If you are running OctoPrint, you do not need to make any slicer changes. 
:::

Celestrius will watch your print during the first layer to make sure nothing fishy like poor adhesion, under/over extrusion, blobbing and other issues are present. After the first layer is completed, the print will be paused and a first layer scan will be completed. After the first layer scan is completed, you will get an email with a report card on your first layer.

In order to make this work, Celestrius needs to be able to know when the first layer is printing and when it finishes. To make this happen, you'll need to adjust your slicer settings to include a macro written to help conduct the first layer scan. 

## Configure Layer Scanning: 

In addition to colllecting images while the first layer prints, you can use a layer scan macro to have Obico's first layer Ai scan the print after the first layer finishes to get a better analysis of the first layer as a whole. 

Follow these steps to configure your setup for first layer scanning: 

## Update the Obico Plugin to version 1.5.2-5. 
First, update the Obico plugin to the latest version. When you update the moonraker-obico plugin, we will automatically make two adjustments to your klipper setup:
1. Add ```moonraker_obico_macros.cfg``` to your Config Files. This file contains the layer scan macro. 
2. Add ```[include moonraker_obico_macros.cfg]``` to your ```printer.cfg``` file.

## **Choose your slicer below and make the changes detailed in the section for your slicer** {#choose-your-slicer-below-and-make-the-changes-detailed-in-the-section-for-your-slicer}

## Slicer Configuration
We already added some custom g-code to the slicer to get the layer information to be passed from the slicer. Now, we will add one more line to the "Before Layer Change" section of the slicer. 

<Tabs>
<TabItem value="PrusaSlicer" label="PrusaSlicer" default>

1. Open PrusaSlicer

2. Go to the *Print Settings* tab.

3. Click *Custom G-Code*
   
4. Add the following line to the "Before layer Change" section: ```_OBICO_LAYER_CHANGE CURRENT_LAYER={layer_num + 1} MINX=[first_layer_print_min_0] MINY=[first_layer_print_min_1] MAXX=[first_layer_print_max_0] MAXY=[first_layer_print_max_1]```

</TabItem>
<TabItem value="SuperSlicer" label="SuperSlicer">
1. Open SuperSlicer

2. Go to the *Print Settings* tab.

3. Click *Custom G-Code*
   
4. Add the following line to the "Before layer Change" section: ```_OBICO_LAYER_CHANGE CURRENT_LAYER={layer_num + 1} MINX=[first_layer_print_min_0] MINY=[first_layer_print_min_1] MAXX=[first_layer_print_max_0] MAXY=[first_layer_print_max_1]```

</TabItem>
<TabItem value="OrcaSlicer" label="OrcaSlicer">
1. Open OrcaSlicer

2. Click the edit printer button. It's the button next to the wifi symbol.

3. Click *Machine G-Code*

4. Add the following line to the "Before layer Change" section: ```_OBICO_LAYER_CHANGE CURRENT_LAYER={layer_num + 1} MINX=[first_layer_print_min_0] MINY=[first_layer_print_min_1] MAXX=[first_layer_print_max_0] MAXY=[first_layer_print_max_1]```

</TabItem>
<TabItem value="Cura" label="Cura">
At this time, we do not support first layer scanning in Cura. It's custom g-code is not as robust as other slicers so we didn't have a straightforward solution, but we let us know if you use Cura, and we will try to come up with a solution if enough users are using Cura. Instead of configuring cura for the first layer scan, you'll need to configure it to output the current layer so Obico knows when the first layer finishes. *Thanks to Pedro Llamas for his Klipper Pre-processor script and detailed instructions. *

1. Open Cura

2. Open the "Help" menu and click *Show Configuration Folder*

3. On the file list, open the *Scripts* folder

4. Download ```KlipperPreprocessor.py``` to the "scripts" folder

5. Close the file list

6. Close Cura

7. (optional) Download ```preprocess_cancellation``` to a folder of your choice

8. (optional) Download ```klipper_estimator``` to a folder of your choice

9.  Open Cura

10. Open the *Extensions* menu, then *Post Processing*, and click on *Modify G-Code*

11. Click on *Add a script* and select *Klipper Preprocessor*

12. Set options according to your needs (hover any option to view the description)

13. Click *Close* when finished

</TabItem>
</Tabs>


Layer scanning is currently not supported for Cura. It may be added in the future.

## Layer Scanning Configuration Options

![](/img/user-guides/first-layer-scan-configuration-settings.png)


The following options are available to be configured in the [Celestrius Alpha Enrollment page](https://app.obico.io/ent/celestrius_alpha_enroll/).: 

1. **Enable or Disable**: Enable or disable the first layer scan by clicking the checkbox (Scanning is enabled by default). If you turn off scanning, first layer AI will still work, but it may be more accurate with scanning enabled. 
2. **Retraction Value**: This is the amount that your filament will retract after the first layer finishes printing. This helps prevent filanent ooze during the scan. The default is 6.5mm.
3. **Scan Height**: The Z-height that the scan will run at. The default value is 4mm. If your camera is out of focus while doing the first layer scan, adjust the height so your camera is in focus. 