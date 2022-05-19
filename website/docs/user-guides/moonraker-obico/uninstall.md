---
title: Uninstall Obico for Klipper
---

To completely uninstall Obico for Klipper, run these command

```
sudo systemctl stop moonraker-obico.service
sudo systemctl disable moonraker-obico.service
sudo rm /etc/systemd/system/moonraker-obico.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
rm -rf ~/moonraker-obico
```

You many need to adjust the paths based on your specific setup.
