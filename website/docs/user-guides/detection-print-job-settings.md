---
id: detection-print-job-settings
title: Printer settings
sidebar_label: Printer settings
---

For most users, the default settings in The Spaghetti Detective is good enough. However, if you have adventurous mind, you can fine-tune them to fit your needs.

To access these settings

1. From the printer screen, click the kebab menu (**⋮**) on the top right of the screen.
2. Click "**Configure 🔧**"

![Printer Settings Menu](/img/user-guides/helpdocs/printer_settings_menu.png)

## When potential failure is detected {#when-potential-failure-is-detected}

This part of the settings tells The Detective how to react when a potential failure is detected.

:::info
The Detective makes mistakes and some times sends out false alarms. [Learn more about false alarms](/docs/user-guides/failure-detection-false-alarms).
:::

- **Just notify me via email and text.** Quite self-explanatory. When you choose this option, The Detective will NOT freak out when she sees a potential print failure. She will just calmly sends you an email (and a text if you have your phone number on file) and be done with it.

- **Pause the print and notify me via email and text.** With this you are telling The Detective to be more proactive. When she thinks she sees a crime scene, she will pause your print to prevent further damage.

## When print is paused {#when-print-is-paused}

:::caution
Advanced settings. If you are not sure how this setting may effect your printer, we recommend leaving it as is.
:::

Pausing a print is actually a little complex. Since it's possible that your print may be paused for quite long time before you get to it (for example, The Detective pauses the print while you are sleeping), we don't want to just stop the motor movement and leave the hotend high and dry (in this case it's more like high and hot). Instead, we want to give you the options to make sure no further damage will be caused to your printer, and the print quality is preserved as much possible.

- **Turn off hotend heater(s).** If checked, The Detective will turn off the heater (or all heaters if your printer has more than one) when the print is paused. She will also make sure the heater(s) are warmed up to the target temperature *BEFORE* any motor is set in action. We can't think of any reasons why you would want to uncheck this box except that you already have a GCode script in OctoPrint to get this taken care of.

- **Turn off bed heater.** Similarly, you can tell The Detective to turn off bed heater after a print is paused. However, you may not want to have this box checked, especially if you often print with ABS. Cooling off the bed for any extended period of time will almost certainly cause ABS to warp and/or have bed-adhesion problem. Again, if this option is checked, the bed will be warmed up to target temperature before any motor is set in action.

- **Retract filament by xx mm.** If checked, the filament will be retracted by the specified distance when a print is paused. This option, combined with the next one, will minimize the impact on print quality from pausing the print. The filament will be de-retracted by the same distance on resume.
:::danger
Please do NOT check this if you already have pause/resume GCode scripts in OctoPrint, as it may cause unpredictable behavior at the moment of pause and resume.
:::

- **Lift extruder along Z axis by yy mm.** If checked, the extruder will lift along the Z-axis by the specified distance, to best preserve the print quality. When the print is resumed, the extruder will be lowered to the previous height before the pause.
:::danger
Similar to retraction, please do NOT check this if you already have pause/resume GCode scripts in OctoPrint, as it may cause unpredictable behavior at the moment of pause and resume.
:::

## How alerted do you want the Detective to be on this printer? {#how-alerted-do-you-want-the-detective-to-be-on-this-printer}

:::caution
Advanced settings. If you are not sure how this setting may effect your printer, we recommend leaving it as is.
:::

We all know [The Detective makes mistakes](/docs/user-guides/failure-detection-false-alarms/), we want to give you an option to decide how aggressively she needs to be looking for something fishy (or cheesy if that's the flavor of your spaghetti).

Drag the slider around to see what each alertness level would give you. Our suggestion is to keep it at "**Medium**" (the default) to start with. If after a few prints, The Detective has been annoying you with too many false positives, set it to low and you should receive fewer alerts. Conversely, if The Detective has missed some delicious spaghetti, you may want to set the level higher.
