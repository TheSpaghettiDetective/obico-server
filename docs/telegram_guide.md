# Telegram Setup Guide

My Base: Fresh Install Ubuntu 20.04.

You need to open a terminal with your device. I am doing this via SSH (I'm using Putty on windows).

1. Install nmp
```sh
sudo install npm
```
![install nmp](img/telegram/installnpm.JPG)

2. Install looptools
```sh
sudo install looptools
```
![loop](img/telegram/installloop.JPG)


3. Install localtunnel and run it
```sh
npx localtunnel --port 3334
```
![INSTALL tunnel](img/telegram/starttunnel.JPG)
![RUNNING loop](img/telegram/localtunnelrun.JPG)

4. Open telegram (I`m using windows telegram app) and find botfather

![BOT FATHER](img/telegram/findbot.JPG)

5. Start conversation and open a menu
```
/start
```
![botcommands](img/telegram/botcommands.JPG)

6. Create your own bot and give him name
```
/newbot
```
![bot name](img/telegram/botname.JPG)

7. Get BOT ID and TOKEN

![token](img/telegram/id.JPG)

8. Set domain which was given by tunnel in Step 3
```
/setdomain
```
![set domain](img/telegram/domain.JPG)

9. Add TOKEN with ID in docker-compose.yml

    - Open the file:
        - Option 1: Edit docker-compose.yml through terminal
        ```shell
        cd TheSpaghettiDetective
        sudo nano docker-compose.yml
        ```
        ![find docker config](img/telegram/getconfig.JPG)
        - Option 2: edit it directly
            - Find the folder called `TheSpaghettiDetective` in your home directory
            - Open it. Inside you should find a file called `docker-compose.yml`. Open it.

    - Edit the file to include your ID
    ![config](img/telegram/config.JPG)

  
10. Reboot Docker
```sh
cd TheSpaghettiDetective
sudo docker-compose down
sudo docker-compose up -d
```
![reboot](img/telegram/reboot.JPG)

11. Go on your TSD server VIA link connected to Telegram.

Go in preferences and connect to Telegram.

![linking](img/telegram/linkbot.JPG)

12. Push Test button after

RESULTS

![Results](img/telegram/result.JPG)