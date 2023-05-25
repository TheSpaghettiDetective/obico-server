#!/bin/bash -e

sudo apt update && sudo apt install -y libhdf5-dev libssl-dev python3-pip
sudo systemctl restart docker
sudo pip3 install --upgrade pip setuptools wheel
sudo pip3 install docker-compose

cat <<EOT >docker-compose.override.yml
version: '2.4'

services:
  ml_api:
    runtime: nvidia
EOT

sudo docker-compose up -d

sudo systemctl enable docker

while true; do
  read -p "Would you like to configure this Jetson Nano so it can be addressed by 'obico.local' on your local network? [N/y/d]: " -e -i "N" ynd
  case $ynd in
    [Yy]* ) sudo $(dirname "$0")/avahi_setup_jetson.sh; break;;
    [Nn]* ) break;;
    [Dd]* ) echo "Read More Here: https://www.obico.io/docs/server-guides/configure/";;
  esac
done
