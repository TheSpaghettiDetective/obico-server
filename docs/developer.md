# Developer Guide

How to set up a simple development environment. 

## Docker Compose Modifications

To have a simple and easy octoprint with a virtual server, add the following to the docker-compose file:

```
  octoprint:
    image: octoprint/octoprint
    restart: unless-stopped
    ports:
      - 8080:80
    volumes:
      - octoprint:/octoprint
```

Also, in the "web" servive, modify the "command" entry to remove "-noreload".  This gets the web server
to reload itself whenever it detects a python file is updated.

## Getting Started

To run TSD in developer mode:

1. ```make build-images```
1. ```make vue-live```
1. Open another terminal, and run ```make frontdev-up```

After that:

1. Log into TSD Admin and set it up as you would normally.
1. Log into octoprint, set it up to allow a virtual 3d printer.  
1. Install the TSD plugin.
1. Connect TSD Plugin to the dev instance of TSD.

Optional Steps:

If you want to run two instances of TSD, then make two different folders as shown below.

```
<parent_folder>/TheSpaghettiDetective
<parent_folder>/TheSpaghettiDetective_develop
```

Run, the first TSD instance normally. Don't change anything. In the second folder with "_develop", simply
change the ports in the docker compose file to be something other than 3334.  Afterward, start up the 
develop TSD beside the regular one.  

## Developing at the same time as Octoprint TSD Plugin

Both repositories will have to be put on an overlay network.  

Add the following to each docker-compose.yml file. This will set the default network to an
attachable overlay network for each service.  

```
networks: 
  default: 
    external: 
      name: tsd_overlay
```

Run this command:

```
docker network create -d overlay --attachable tsd_overlay
```

Then, run the start up functions for each repository.