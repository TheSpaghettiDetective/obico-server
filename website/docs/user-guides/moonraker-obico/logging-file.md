---
title: Troubleshoot issues using the log file
---

The log file is usually located in the folder `~/printer_data/logs/`. The name of the log file is usually `moonraker-obico.log`. If you have multiple Moonraker running, the file name will be `moonraker-obico-xxxx.log`. The `-xxxx` part is the port of your Moonraker service listens on. You will need to look for the log file that is corresponding to their own ports.

If the log file doesn't provide enough info for you to find the root cause of the issue, it can often be very helpful to change the logging level to `DEBUG`. Follow [this guide](../config/#logging-section) to configure logging settings. Don't forget to restart the moonraker-obico service after the change.

:::caution
You need to restart the printer or Raspberry Pi for any change to take effect.
:::

:::caution
When you set the logging level to `DEBUG`, the log file will become very large quickly.
:::

## Download the log file to view it {#download-the-log-file-to-view-it}

### If you are using Mainsail {#if-you-are-using-mainsail}

1. Go to the "MACHINE" tab in the Mainsail UI. Select "Logs" from the dropdown.

1. Locate the `moonraker-obico.log` file.

1. Select the file and click the download button.

![](/img/user-guides/helpdocs/download-moonraker-obico-log-mainsail.png)


### If you are using Fluidd {#if-you-are-using-fluidd}

1. Go to the "Configuration" tab in the Fluidd UI.

1. Locate the `moonraker-obico.log` file.

1. Right click the file and select "Download".

![](/img/user-guides/helpdocs/download-moonraker-obico-log-fluidd.png)
