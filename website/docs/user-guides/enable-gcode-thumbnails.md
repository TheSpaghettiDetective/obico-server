---
id: enable-gcode-thumbnails
title: How to Enable G-Code Thumbnails in Your Slicer
sidebar_label: Enable G-Code Thumbnails
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

![](/img/user-guides/gcode-thumbnails/obico-gcode-thumbnails.png)

Most 3D printing slicers allow the ability to include preview thumbnails that can be shown in the Obico mobile and web app, as well as Mainsail and KlipperScreen.

:::caution
Obico shows thumbnails only for G-Codes, uploaded directly to the app. If you explore OctoPrint/Klipper files, you won't see file previews.
:::

Each slicer handles thumbnails differently. Select the slicer you use below to enable thumbnails.

<Tabs groupId="operating-systems">
  <TabItem value="Prusa" label="Prusa Slicer (2.3.0+)">

![](/img/user-guides/gcode-thumbnails/prusa-slicer-1.png)

1. In *Expert Mode*, select *Printer Settings*

![](/img/user-guides/gcode-thumbnails/prusa-slicer-thumbnail.png)


2. Under the *Thumbnails* section, enter `32x32` for *Small* and `400x300` for *Big*. You can further customize your thumbnail's look in SuperSlicer as well.


  </TabItem>
  <TabItem value="Cura" label="Cura">

In Cura, there are two options for enabling thumbnails.

**In Cura 4.9+, you can use a post processing script**

![](/img/user-guides/gcode-thumbnails/cura-post-process.png)

1. In Cura, navigate to `Extensions > Post-Processing, Modify G-Code`
2. Click *Add a script*. Click *Create Thumbnail*.
3. Enter `32x32` for the value.
4. Repeat steps two and three to create a thumbnail with size `400x300`.
5. Save the changes.

**In Cura 4.7+, you can install Cura2Moonraker**

This plugin allows you to enable thumbnails among other things such as the ability to print from your slicer directly to Mainsail.

Follow the instructions in the [Cura2Moonraker Github Repository](https://github.com/emtrax-ltd/Cura2MoonrakerPlugin) if you prefer this method.


  </TabItem>
  <TabItem value="SuperSlicer" label="Super Slicer">

1. In *Expert Mode*, select *Printer Settings*

![](/img/user-guides/gcode-thumbnails/super-slicer-thumbnails.png)


2. In *General* under the *firmware section*, enter `32x32, 400x300` for *G-Code thumbnails*. If an option is available, set the *format of G-code thumbnails* to `png`. These values should work for the Obico mobile and web app as well as Mainsail and KlipperScreen.



  </TabItem>
  <TabItem value="ideamaker" label="ideaMaker">

![](/img/user-guides/gcode-thumbnails/ideamaker-thumbnails.png)

1. Click *Printer* at the top of the screen, and then click *Printer Settings*.

![](/img/user-guides/gcode-thumbnails/ideamaker-thumbnails-1.png)

2. Click the advanced tab. Check the box titled *Gcode thumbnails for OctoPrint and Mainsail*
3. Set the values to `300x300` or similar. Ensure the values are the same.




  </TabItem>
</Tabs>
