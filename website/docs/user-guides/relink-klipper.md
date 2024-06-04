---
title: Re-link Klipper-based printer
---

## If you don't need to change to a different Obico server {#if-you-dont-need-to-change-to-a-different-obico-server}

Re-linking process is very similar to [the initial setup process](/user-guides/klipper-setup.md).

1. SSH to the Raspberry Pi (or other SBC) your Klipper runs on.
2. Run:

```bash
    cd ~/moonraker-obico
    ./install.sh
```

3. You will be asked to confirm your Moonraker host and port, exactly the same the initial setup process.
4. The installation script will bring you to the final step to enter the 6-digit code. Find the code in the same way as in the  initial setup process.

## If you need change to a different Obico server {#if-you-need-change-to-a-different-obico-server}

### Change the Obico server setting {#change-the-obico-server-setting}

1. Open `moonraker-obico.cfg` in Mainsail/Fluidd.
2. Change the `url = ` line inside the `[server]` section. Remember the format should be `http(s)://full_server_domain_name_or_ip_address:port_if_not_80`
3. SSH to the Raspberry Pi (or other SBC) your Klipper runs on.
4. Run:

```bash
    cd ~/moonraker-obico
    ./install.sh
```

5. You will be asked to confirm your Moonraker host and port, exactly the same the initial setup process.
6. The installation script will bring you to the final step to enter the 6-digit code. Find the code in the same way as in the  initial setup process.

