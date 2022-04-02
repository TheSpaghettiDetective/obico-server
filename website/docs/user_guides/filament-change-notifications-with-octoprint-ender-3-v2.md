---
id: filament-change-notifications-with-octoprint-ender-3-v2
title: "Recompile the firmware to enable HOST_ACTION_COMMANDS for Creality Ender 3 V2, or Ender 3 V1 upgraded to a 32-bit mainboard"

---

## What you need

Thanks to the new mainboard on the Ender 3 V2, you won’t need much to update its firmware:

- A Micro SD card.
- A laptop or a desktop computer. Either Mac or Windows will work.

## Step 1: Install required software

First,  lets install all of the necessary programs. All of these programs have Mac and Windows versions available.

1. Install [Python](https://www.python.org/downloads/release/python-382/).

1. Install [Microsoft Visual Studio Code](https://code.visualstudio.com/download) and open it.

1.  In VSCode, install the [Auto Build Marlin](https://marketplace.visualstudio.com/items?itemName=MarlinFirmware.auto-build) extension.

1.  Click the extensions button on the left side of VSCode and type ‘Auto Build Marlin’ and click to install it. Platform.io will also be installed at this time.

1. Close and reopen VSCode to ensure the extensions you just installed are active.

![Open Platform.io](/img/user_guides/filament-change/home-button-vscode.PNG)


## Step 2: Download the latest Marlin source code and configure it

1. Download [Marlin](https://marlinfw.org/meta/download/). Most likely, you will want the latest version, which is 2.0.9.3 at this time. Make sure you download the both “Marlin-2.0.x.zip” and “Configurations-release-2.0.x.x.zip”.

1. After downloading, extract the zip file.

1. Find the configuration.h and configuration.adv files for your printer.

1. Copy and paste the files into the .\Marlin folder that is in the Marlin 2.xx folder that you unzipped in the previous step.

1. When prompted, choose to overwrite the two files that are already there.

1. Neil please can you please the above steps more specific to ender v2?


## Step 3: Enable HOST_ACTION_COMMANDS and M600

1.  Click the *home symbol* on the bottom left of the screen to open Platform.io.

![Open Project Platform.io](/img/user_guides/filament-change/open-project-platform-io.PNG)

2. Click the *Open Project* button.

3. Find the unzipped Marlin folder and click *Open*

4. Click the *Explorer* button on the left side and edit the configuration_adv file in the Marlin folder.

5. To enable the M600 command, type *control-f* on your keyboard, and search for *M600* to find where it is listed in the file.
 
6. Delete the two `/` symbols in front of `#define ADVANCED_PAUSE_FEATURE`

![Enable M600](/img/user_guides/filament-change/advanced-pause-m600.png)

7. To enable Host Action Commands Type *control-f* again and search for host action command. Scroll down until you see *Host Action Commands*

8. Delete the `/` symbol in front of `#define HOST_ACTION_COMMANDS`

![Host Action Commands](/img/user_guides/filament-change/host-action-commands.png)

9. Save the file


## Step 4: Compile the firmware

1.  Hover over the build section on the top left side of the screen and you will see a hammer icon. Click this icon and click Build on the right to start building the firmware.

:::note

Be patient, compiling the firmware can take as long as ten minutes.

:::

2.  At the end of the terminal, you should see a list of boards, with most of them saying Ignored, and your board listed as Success.

## Step 5: Flash the new firmware

1. Go to your “Marlin-2.0.x” folder, 

1. Go to the folder where you extracted Marlin, find and open the “.pio” folder.

1. Open the build folder and then open the folder with a name beginning with “STM32” (names might vary depending on the mainboard).

1. Find and copy the most recent (by time) BIN file. Make sure not to change the firmware’s name, as it won’t work if the name is changed.

1. Plug in your mainboard’s Micro SD card into your device.

1. Clear (delete or move) everything on it.

1. Save the BIN firmware file to the Micro SD card.

1. Neil can you check to confirm the steps above?
