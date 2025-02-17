---
id: filament-change-notifications-with-octoprint-ender-3-v2
title: "Recompile the firmware to enable HOST_ACTION_COMMANDS for Creality Ender 3 V2, or Ender 3 V1 upgraded to a 32-bit mainboard"

---

## What you need {#what-you-need}

Thanks to the new mainboard on the Ender 3 V2, you won’t need much to update its firmware:

- A Micro SD card.
- A laptop or a desktop computer. Either Mac or Windows will work.

## Step 1: Install required software {#step-1-install-required-software}

First,  lets install all of the necessary programs. All of these programs have Mac and Windows versions available.

1. Install [Python](https://www.python.org/downloads/release/python-382/).

1. Install [Microsoft Visual Studio Code](https://code.visualstudio.com/download) and open it.

1.  In VSCode, install the [Auto Build Marlin](https://marketplace.visualstudio.com/items?itemName=MarlinFirmware.auto-build) extension.

1.  Click the extensions button on the left side of VSCode and type ‘Auto Build Marlin’ and click to install it. Platform.io will also be installed at this time.

1. Close and reopen VSCode to ensure the extensions you just installed are active.

![Open Platform.io](/img/user-guides/filament-change/home-button-vscode.PNG)


## Step 2: Download the latest Marlin source code and configure it {#step-2-download-the-latest-marlin-source-code-and-configure-it}

1. Download [Marlin](https://marlinfw.org/meta/download/). Most likely, you will want the latest version, which is 2.0.9.3 at this time. Make sure you download the both “Marlin-2.0.x.zip” and “Configurations-release-2.0.x.x.zip”.

2. After downloading, extract the zip file.

3. Find the configuration.h and configuration.adv files for your the Creality Ender 3V2.

:::tip

If you don't have a Creality Ender 3V2, go to our general guide for 32 bit boards

:::

4. In the examples folder, select Creality. then select Creality Ender 3V2. You will see

5. Copy and paste the files into the .\Marlin folder that is in the Marlin 2.xx folder that you unzipped in the previous step.

6. When prompted, choose to overwrite the two files that are already there.

## Step 3: Set the correct Environment {#step-3-set-the-correct-environment}

1.  Click the *home symbol* on the bottom left of the screen to open Platform.io.

![Open Project Platform.io](/img/user-guides/filament-change/open-project-platform-io.PNG)

1. Click the *Open Project* button.

1. Find the unzipped Marlin folder and click *Open*

1. Click the *Explorer* button on the left side, and click the platform.ini menu

1. Navigate to the Marlin Folder on the left side of the screen.

![Find pins.h](/img/user-guides/filament-change/find-environment-for-board-marlin-ender-3-v2.jpg)

1. Select the *Marlin* folder. Select *pins*. Select *pins.h*

1. Type control-f and then search for your mainboard manufacturer. The Ender 3 V2 comes stock with a Creality 4.2.2 32-bit mainboard.

![Find the environment for your mainboard](/img/user-guides/filament-change/platformio-environment-for-creality-ender-3v2.jpg)

1. Copy the environment corresponding to your board as shown.

![Enter the correct environment](/img/user-guides/filament-change/creality-ender-3-v2-marlin-environment.jpg)

1. Replace the default_envs with the environment you found in the previous step.  For the Creality Ender 3 V2 with the 4.2.2 32-bit mainboard, it the value is: default_envs = STM32F103RET6_creality



## Step 4: Enable HOST_ACTION_COMMANDS and M600 {#step-4-enable-host_action_commands-and-m600}

1. Click the *Explorer* button on the left side and edit the configuration_adv file in the Marlin folder.

1. To enable the M600 command, type *control-f* on your keyboard, and search for *M600* to find where it is listed in the file.

1. Delete the two `/` symbols in front of `#define ADVANCED_PAUSE_FEATURE`

![Enable M600](/img/user-guides/filament-change/advanced-pause-m600.png)

1. To enable Host Action Commands Type *control-f* again and search for host action command. Scroll down until you see *Host Action Commands*

1. Delete the `/` symbol in front of `#define HOST_ACTION_COMMANDS` and any other necessary symbols so yours looks identical to the image shown below.

![Host Action Commands](/img/user-guides/filament-change/host-action-commands.png)

1. Save the file


## Step 5: Compile the firmware {#step-5-compile-the-firmware}

1.  Click the Marlin icon on the left side of the screen and hover over the build section on the top left side of the screen and you will see a hammer icon. Click this icon and click Build on the right to start building the firmware.

:::note

Be patient, compiling the firmware can take as long as ten minutes.

:::

2.  At the end of the terminal, you should see a list of boards, with most of them saying Ignored, and your board listed as "Success".

## Step 6: Flash the new firmware {#step-6-flash-the-new-firmware}

1. Go to your “Marlin-2.0.x” folder,

1. Go to the folder where you extracted Marlin, find and open the “.pio” folder.

1. Open the build folder and then open the folder with a name beginning with “STM32” (names might vary depending on the mainboard).

1. Find the most recent (by time) BIN file. You must change the name to a unique name other than "firmware.bin." For example, a suitable name would be "mfirmware.bin" Once you have changed the name, copy the .bin file.

1. Plug in your mainboard’s Micro SD card into your device.

1. Clear (delete or move) everything on it.

1. Save the BIN firmware file to the Micro SD card.
