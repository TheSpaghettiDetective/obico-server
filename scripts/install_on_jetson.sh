#!/bin/bash -e

distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-docker2 python python-pip curl libffi-dev python-openssl libssl-dev zlib1g-dev gcc g++ make
sudo systemctl restart docker
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

while true; do
    printf "Would you like to change the address hostname it is accesible at obico.local?\nYes/No (yN)\tDetails (d) "
	read -p " " ynd
    
    case $ynd in
        [Yy]* ) sudo ./avahi_setup_jetson.sh; break;;
        [Nn]* ) break;;
        [Dd]* ) echo "Read More Here: https://www.obico.io/docs/server-guides/configure/";;
        * ) echo "Please answer yes or no.";;
    esac
done
