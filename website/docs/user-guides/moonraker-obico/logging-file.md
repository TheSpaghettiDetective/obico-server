---
title: Troubleshoot issues using the log file
---

The log file is usually located in the folder `~/klipper_logs/moonraker-obico-7125.log`. Here the `-7125` part is the port of your Moonraker service listens on. If you have multiple Moonraker running, you will need to look for the log file that is corresponding to their own ports.


If the log file doesn't provide enough info for you to find the root cause of the issue, it can often be very helpful to change the logging level to `DEBUG`. Follow [this guide](config.md/#logging-section) for detailed instructions. Don't forget to restart the moonraker-obico service after the change.

:::caution
When you set the logging level to `DEBUG`, the log file will become very large quickly.
:::
