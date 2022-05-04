---
title: Fun project with NVIDIA Jetson Nano - AI failure detection for 3D printing
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
description: Put your NVIDIA Jetson Nano to real use that brings you some practical benefit. Run an AI failure detection for your 3D printer.
tags: ['3D Printng Tips and Tricks', 'How-To']
---

The Spaghetti Detective uses AI (Deep Learning) to detect 3D printing failures. Compared to a CPU that runs in most PCs, GPU is much faster and more power-efficient at running the Deep Learning model in TSD. GPUs are commonly found in gaming PCs. However, even an entry-level gaming that can run TSD private server can easily set you back $1,000+. Ouch!

Are there an inexpensive GPUs that can be used to run TSD private server? Yes! [NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit) is a popular option among people who run TSD private servers. It is a single board computer so it can run TSD private server all by itself. The best part? It's quite affordable. Even if you throw in other things such as power supply, NVIDIA Jetson Nano will let you run TSD private server with less than $150!

If you are one of the people who want to jump on the Deep Learning bandwagon by doing a fun project, and you don't want to break the bank, follow along!

<!--truncate-->

## Hardware prerequisite

- NVIDIA Jetson Nano. **Important: Please get the model with 4GB memory. The 2GB model doesn't have enough memory to run TSD private server.**
- Micro SD card. 16GB minimum.
- Micro USB charger/power supply. 2A minimum. *Many* chargers over-label their amperage. So make sure you use one that can *really* output 2A or more.
- Ethernet cable (to connect to your network router).
- HDMI cable (to connect to a monitor).
- USB keyboard.
- USB mouse.

## Flash the Micro SD card

1. Go to the [NVIDIA JetPack SDK official website](https://developer.nvidia.com/embedded/jetpack).

2. Download the JetPack SD card image. Make sure the JetPack version is 4.5.1 or higher. NVIDIA may require you to register a free account before they give you the download link (I know... I don't like that either!).

![](/img/blogs/jetson/jetson_2.png)

3. Flash the image to the Micro SD card using balenaEtcher (or any other method of your choice). Download balenaEtcher [here](https://www.balena.io/etcher/).

![](/img/blogs/jetson/jetson_1.png)

## Connect NVIDIA Jetson Nano and boot it up

1. Insert the Micro SD card into the card slot.

![](/img/blogs/jetson/jetson_3.jpg)

2. Connect all cables.

![](/img/blogs/jetson/jetson_4.jpg)

3. Now the NVIDIA Jetson Nano should boot up. You will need to go through a few steps to set up basic things like timezone and user name. Nothing too exciting here.

## Install The Spaghetti Detective server

1. Double-click the "Terminal" icon the NVIDIA Jetson Nano's desktop. This will drop your cursor at a commend line prompt.

2. Copy-paste the following commands at the prompt:

```
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
cd TheSpaghettiDetective
./scripts/install_on_jetson.sh
```

3. Go grab a coffee. Step 2 will take 15-30 minutes.

## Obtain the IP address of your NVIDIA Jetson Nano

1. Click the "Connection Information" on the system menu

2. Select the "Wired connection 1 (default)" tab.

3. Find the value of the "IP Address" row. Write down this IP address as you will need later on. In this screenshot, my IP address is `192.168.0.120`. In this guide I'll use `your_server_ip` to represent this value.

![](/img/blogs/jetson/jetson_5.png)

## Configure The Spaghetti Detective server

1. Open another computer, open the browser. Enter `http://your_server_ip:3334/admin/` in this address bar. You will be asked to login. Use the default email address `root@example.com` and default password `supersecret` to login.

![](/img/blogs/jetson/jetson_6.png)

2. `root@example.com` is the super admin of your TSD server. To keep it secure, once you have logged in, go to `http://your_server_ip:3334/admin/app/user/1/password/` to change the password.

3. In the same browser window, go to the address `http://your_server_ip:3334/admin/sites/site/1/change/`. Change "Domain name" to `your_server_ip:3334`. No "http://", "https://" prefix or trailing "/", otherwise it will NOT work.

![](/img/blogs/jetson/jetson_7.png)

4. Now the server is ready. Go to `http://your_server_ip:3334/` to add a printer to your server.

![](/img/blogs/jetson/jetson_8.png)


## Link OctoPrint to your own awesome The Spaghetti Detective private server!

The process to link OctoPrint to TSD private server is almost the same as the [Setup Guide](/docs/user_guides/octoprint-plugin-setup), except one setting: the "Server Address" needs to be set as `http://your_server_ip:3334`.

![](/img/blogs/jetson/jetson_9.png)

After the linking process is successful, restart the OctoPrint, refresh The Spaghetti Detective printer page, and you should see something similar to this:

![](/img/blogs/jetson/jetson_10.png)

Hooray! Now you can enjoy the peace of mind while printing, thanks to The Spaghetti Detective server and NVIDIA Jetson Nano!
