---
title: The Spaghetti Detective on Jetson Nano - A complete installation guide
author: MidnightLink
author_url: https://www.reddit.com/user/MidnightLink/
tags: ['How-To']
---

:::danger
This guide is out of date. The steps to install The Spaghetti Detective private server on a Jetson Nano have been greatly simplified and as the result, this guide no longer works. Please head to [the updated guide](https://www.thespaghettidetective.com/blog/2021/06/06/nvidia-jetson-nano-fun-project-3d-printing/).*
:::

*Reddit user MidnightLink took the time to write and post [an awesome guide on Reddit](https://www.reddit.com/r/3Dprinting/comments/g2kwvn/jetson_nano_spaghetti_detective_a_complete/). Re-posting it here with his permission. Thank you MidnightLink!*

Hey all! The other day I decided I wanted to run a dedicated TSD server at my home as I have 4 printers that I want to monitor, and no real want to send out a bunch of info to an unknown server. Looking into the options, and not wanting to have my PC on 24/7, I picked up a Jetson Nano and started working on getting it ready.

The instructions on the official GitHub for doing this are very lacking, and a lot of the commands don't work properly. (docker-compose for example is a MASSIVE pain as it's not native to ARM64, and there are a decent amount of missing dependencies) so here is the complete guide on how to set up your own Spaghetti Detective server on a Jetson Nano!

<!-- truncate -->

I've made this guide as easy as possible, so some things are dumbed down.

This is all on the consideration that you are going to run this hooked into a spare Ethernet port on your router/switch, and are setting up from a Windows environment.

## Parts/Software list:

- Jetson Nano https://developer.nvidia.com/buy-jetson
- Power supply (this is what I used) https://www.amazon.com/gp/product/B01N4HYWAM/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1
- Micro USB cable
- Micro SD Card (I'd recommend 32GB or larger)
- Any kind of MicroSD Adapter to plug into your PC
- Putty https://www.chiark.greenend.org.uk/~sgtatham/putty/
- WinSCP https://winscp.net/eng/index.php
- Etcher https://www.balena.io/etcher/
- Modified docker-compose.yml file https://github.com/MidnightLink/TSDJetsonNano
- The latest SD Card Image from here https://developer.nvidia.com/embedded/downloads
- Optional: A case. You can either 3D print one https://www.thingiverse.com/thing:3518410 or purchase one off of Amazon

Before you begin make sure that the jumper on the board is set up to accept the power from the PSU, not from USB. My jumper came already in place but just needed flipped upside-down.

## Good? Good! Let's start.

1. Flash the Jetson's SD card image using Etcher
1. Put the micro SD back into the Jetson Nano. Plug in your ethernet cable, usb cable, and power cable. I'd make sure the power cable was plugged in last just to be safe.
1. On your PC go to Device Management, then to the Com Ports drop box. You should soon see a port appear if it hadn't already. This is your Jetson's serial port
1. Open up Putty and to connect through serial
1. Change the COM port to the number found in device manager (COM6 for example), change the baud rate to 115200 then click Open

## You're now connected through serial port directly to the Nano!

1. Go through the initial setup. Tab/enter move around. Choose whatever username/password you'd like. When you get to the network configuration page, tab down and choose eth0
1. The Jetson will reboot and the serial connection will drop. You can now unplug the Jetson from USB and close the Putty connection
1. Find the IP address of your Jetson from your router, open back up Putty and go to that address. Login using whatever username/password you chose during the initial setup.

## Alright, awesome! Now we have access to a SSH command line!

1. First thing's first, lets get everything updated

    `sudo apt-get update -y && sudo apt-get upgrade -y`

2. After all that is finished, we need to install some dependencies.

    ```
    sudo apt-get install -y curl 
    sudo apt-get install -y python-pip
    sudo apt-get install -y python3-pip
    sudo apt-get install -y libffi-dev
    sudo apt-get install -y python-openssl
    ```

## Now to install Docker-Compose.

Since normal install methods are broken as it's not built correctly for ARM64, we will use a precompiled fork.

1. Download the forked docker-compose

    `wget https://github.com/nefilim/docker-compose-aarch64/releases/download/1.25.4/docker-compose-Linux-aarch64`

2. Correctly name it and move it to bin folder

    `sudo mv docker-compose-Linux-aarch64 /usr/local/bin/docker-compose`

3. And give it right permissions to be ran

    `sudo chmod +x /usr/local/bin/docker-compose`

4. Then clone the GIT of TheSpaghettiDetective

    `git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git`

## You will now need to edit the docker-compose.yml file.

You will now need to edit the docker-compose.yml file to include the edits from https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/blob/master/docs/jetson_guide.md as the docker-compose.override.yml file will not work for some reason. If you feel comfortable doing this on your own you can use your favorite text editor (like nano)

1. For simplicity sake this is why I've included WinSCP as a download, and a preconfigured docker-compose.yml file
While leaving Putty open in the background, open up WinSCP
1. Put in your Nano's IP address, username and password then click on Login
1. Go to the TheSpaghettiDetective folder and move the preconfigured docker-compose.yml file into it, making sure to overwrite current file.
1. You can now exit WinSCP
1. Back in Putty run the docker-compose file and let it run. This part will take the longest (15+ minutes)
    
    `cd TheSpaghettiDetective && sudo docker-compose up -d`

1. After you get back to your normal command line, we need to set docker to run at boot with the command

    `sudo systemctl enable docker`

1. And then reboot

    `sudo reboot`


And that's it! After giving the Jetson a good minute or two to reboot, you can now follow the instructions on TSD's github starting at the Basic Server Configuration section: https://github.com/TheSpaghettiDetective/TheSpaghettiDetective#basic-server-configuration



Enjoy!



