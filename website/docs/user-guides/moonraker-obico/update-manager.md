---
id: update-manager
title: Config for Moonraker update manager
---

This should be configured automatically as part of running the `./install.sh` for `moonraker-obico`.

However, if you would like to configure this manually, add the following to your `moonraker.conf`:

```
[update_manager moonraker-obico]
type: git_repo
path: ~/moonraker-obico
origin: https://github.com/TheSpaghettiDetective/moonraker-obico.git
env: /home/pi/moonraker-obico-env/bin/python
requirements: requirements.txt
install_script: install.sh
managed_services:
  moonraker-obico
```

Be sure to update the `env` path in the above to point to Python environment for your `moonraker-obico` installation.
