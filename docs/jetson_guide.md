# Run TSD server on Jetson Nano

Thanks to the work of Raymond, LyricPants, and others, you can now *easily* run a TSD server on a 4GB Jetson Nano.

## Software requirements

The following software is required before you start installing the server:

- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack). If you already flashed a software on you sd card, you will have to replace it with this one. Slow download of the software from Nvidia is normal. **Important:** Before you flash the new software on your sd card, you will have to fully format it first, so make sure you have backed up anything important on an external device.
  - [Flashing Software](https://www.balena.io/etcher/)
  - [SD Card Formater](https://www.sdcard.org/downloads/formatter/)

## Start the Server!

Install the entire server, all in one command!:

*Note: the last JetPack SDK version this has been tested on is jp45.*

*If you succesfully run this on a newer version, please send a message to the official discord and mention @LyricPants66133*

1. Run 
```
git clone https://github.com/LyricPants66133/Jetson_TSD_Fullinstall.git && sh Jetson_TSD_Fullinstall/jetson_TSD_install.sh
```
2. Boot up your favorite streaming service and get a hot drink. This can take a while.

3. Reboot your Jetson to make sure everything is running well: `sudo reboot`

You can then complete setup by following the remaining steps, starting at Basic Server Configuration in [README.md](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective#basic-server-configuration).
