---
title: First Layer AI Slicer Configuration (For Klipper Users Only)
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::warning
Slicer configuration is only required for Klipper. If you are running OctoPrint, you do not need to make any slicer changed
:::

Celestrius will watch your print during the first layer to make sure nothing fishy like poor adhesion, under/over extrusion, blobbing and other issues are present. After the first layer is completed, you will get an email with a report card on your first layer.

In order to make this work, Celestrius needs to be able to know when the first layer is printing and when it finishes. To make this happen, you'll need to adjust your slicer to tell it to pass along the layer information within the G-code file.

## **Choose your slicer below and make the changes detailed in the section for your slicer**


<Tabs>
<TabItem value="PrusaSlicer" label="PrusaSlicer" default>
1. Open PrusaSlicer

2. Go to the *Print Settings* tab.

3. Click *Custom G-Code*

4. Add the following to the top of the *Start G-code* section (before other start G-code): ```SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]```

5. Add the following after the last line of the *End G-code*: ```; total layers count = [total_layer_count]```

6. Add the following to *After Layer Change G-code*: ```SET_PRINT_STATS_INFO CURRENT_LAYER={layer_num + 1}```

Be sure to save the settings to your printer profile so they will be re-used for the duration of the Celestrius Alpha Testing

</TabItem>
<TabItem value="SuperSlicer" label="SuperSlicer">
1. Open SuperSlicer

2. Go to the *Print Settings* tab.

3. Click *Custom G-Code*

4. Add the following to the top of the *Start G-code* section (before other start G-code): ```SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]```

5. Add the following to *After Layer Change G-code*: ```SET_PRINT_STATS_INFO CURRENT_LAYER={layer_num + 1}```

</TabItem>
<TabItem value="OrcaSlicer" label="OrcaSlicer">
1. Open OrcaSlicer

2. Click the edit printer button. It's the button next to the wifi symbol.

3. Click *Machine G-Code*

4. Add the following to the top of the *Machine Start G-code* section (before other start G-code): ```SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]```

5. Add the following to *After Layer Change G-code*: ```SET_PRINT_STATS_INFO CURRENT_LAYER={layer_num + 1}```

6. Add the following after the last line of *Machine End G-code*: ```; total layers count = [total_layer_count]```

</TabItem>
<TabItem value="Cura" label="Cura">
Configuring Cura to get layer information is a bit more involved than PrusaSlicer and SuperSlicer, but thanks to Pedro Llamas Klipper Pre-processor script, and detailed instructions, it can be done!

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
