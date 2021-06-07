#!/bin/bash -e

sudo apt install -y python python-pip curl libffi-dev python-openssl libssl-dev zlib1g-dev gcc g++ make
sudo python -m pip install --upgrade pip setuptools wheel
sudo python -m pip install docker-compose

cat <<EOT >docker-compose.override.yml
version: '2.4'

services:
  ml_api:
    runtime: nvidia
    environment:
        HAS_GPU: 'True'
EOT

sudo docker-compose up -d

sudo systemctl enable docker
