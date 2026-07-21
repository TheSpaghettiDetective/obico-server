#!/bin/bash -e

sudo apt update && sudo apt install -y libhdf5-dev libssl-dev python3-pip
sudo systemctl restart docker

# Prefer the Compose v2 plugin (bundled with modern Docker and JetPack 6);
# fall back to installing docker-compose v1 via pip only on old JetPack
# releases where the plugin is absent. The pip path cannot be the default:
# on Python 3.10+ (JetPack 6) docker-compose 1.29 pins PyYAML 5.4, which no
# longer builds there.
if sudo docker compose version > /dev/null 2>&1; then
  COMPOSE="sudo docker compose"
else
  sudo pip3 install --upgrade pip setuptools wheel
  sudo pip3 install docker-compose
  COMPOSE="sudo docker-compose"
fi

# docker-compose.jetson.yml swaps in the prebuilt L4T inference image and
# enables the nvidia runtime. Passing the files explicitly also makes
# compose ignore any docker-compose.override.yml left behind by an older
# version of this script.
${COMPOSE} -f docker-compose.yml -f docker-compose.jetson.yml up -d

sudo systemctl enable docker

while true; do
  read -p "Would you like to configure this Jetson Nano so it can be addressed by 'obico.local' on your local network? [N/y/d]: " -e -i "N" ynd
  case $ynd in
    [Yy]* ) sudo "$(dirname "$0")/avahi_setup_jetson.sh"; break;;
    [Nn]* ) break;;
    [Dd]* ) echo "Read More Here: https://www.obico.io/docs/server-guides/configure/";;
  esac
done
