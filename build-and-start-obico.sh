#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

## This bash script will 
## 1) Build the container images necessary to run the obico server for the architecture the script is running on
## 2) Run obico-server with the docker-compose-prebuilt.yml uses the previously created container images.

## Defining colors for colored echo output and corresponding functions
green="\e[0;92m"
red="\e[0;91m"
reset="\e[0m"

echo_green() {
    echo -e "${green}$1${reset}"
} 
echo_red() {
    echo -e "${red}$1${reset}"
} 

echo "Starting building process..."
to_build="backend ml_api"
for name in $to_build; do 
    echo_green "Building obico_$name image"
    pushd "$name" || exit 1
    docker build -t "obico_$name" . && echo_green "Building obico_$name successful" || echo_red "Error while building obico_$name"
    popd ... || return
done

while true; do
    read -rp "Do you wish to start obico-server now? Entering \"y\" will run docker-compose up (y/n)" yn
    case $yn in 
        [yY] ) docker-compose -f docker-compose-prebuilt.yml up -d;
            break;;
        [nN] ) echo -e "\nYou can start the obico-server by using \"docker-compose -f docker-compose-prebuilt.yml up -d \" from within the obico-server repository";
            break;;
        * ) echo_red "Please enter (y/n)";;
    esac
done
