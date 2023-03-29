---
title: Uninstall Obico for Klipper
---

To remove the code and system services for Obico for Klipper, run these command

```bash
sudo systemctl stop moonraker-obico.service
sudo systemctl disable moonraker-obico.service
sudo rm /etc/systemd/system/moonraker-obico.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
rm -rf ~/moonraker-obico
```

To remove the configuration:

```bash
rm ~/printer_data/config/moonraker-obico.cfg
rm ~/printer_data/config/moonraker-obico-update.cfg
```

Also edit `~/printer_data/config/moonraker.conf` to remote this line:

`[include moonraker-obico-update.cfg]`

You many need to adjust the paths based on your specific setup.
