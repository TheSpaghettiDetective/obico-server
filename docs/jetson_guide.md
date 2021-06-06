# Run TSD server on NVIDIA Jetson Nano

*If you follow this guide and run into problems, please seek help at: https://discord.gg/NcZkQfj*

## Prerequisites

### Hardware requirements

TSD private server can only run on Jetson Nano 4GB model. The 2GB model doesn't have enough memory to run both the program and load the AI model in the memory.

### Software requirements

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a software on you sd card, you will have to replace it with this one. Slow download of the software from Nvidia is normal. **Important:** Before you flash the new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.
  - [Flashing Software](https://www.balena.io/etcher/)
  - [SD Card Formater](https://www.sdcard.org/downloads/formatter/)

*Note: the last JetPack SDK version this has been tested on is jp45.*

*If you succesfully run this on a newer version, please send a message to the official discord and mention @LyricPants66133*

### Email delivery

You will also need an email account that has SMTP access enabled. For a gmail account, this is [how you enable SMTP access](https://support.google.com/accounts/answer/6010255?hl=en). Other web mail such as Yahoo
should also work but we haven't tried them.

## Get the code and start the server.

1. Get the code:

```
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
```

2. Run it!

```
cd TheSpaghettiDetective
./scripts/install_on_jetson.sh
```

3. Go grab a coffee. Step 2 will take 15-30 minutes.

4. There is no step 4. This is how easy it is to get The Spaghetti Detective up and running (thanks to Docker and Docker-compose).

## Continue to [server configuration the main documentation](../README.md#basic-server-configuration)


*Thanks to the work of Raymond, LyricPants, and others for their contribution!*
