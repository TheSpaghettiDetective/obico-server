  
  

Telegram Step by Step

My Base: Fresh Install Ubuntu 20.04.

  
  

First of all need to install VIA SSH (I`m using Putty)

  

1) install nmp

![install nmp](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/installnpm.JPG) 

2. install looptools

![loop](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/installloop.JPG)

  

3. install localtunnel and run it

![INSTALL tunnel](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/starttunnel.JPG)

![RUNNING loop](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/localtunnelrun.JPG)

  

4. Open telegram (I`m using windows telegram app) and find Find botfather

![BOT FATHER](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/findbot.JPG)

5. Start conversation and menu

![botcommands](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/botcommands.JPG)

6. Create your own bot and give him name

![bot name](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/botname.JPG)

7. Get BOT ID and TOKEN

![token](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/id.JPG)

8. Setdomain which was given by tunnel from Step 3

![set domain](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/domain.JPG)

8. Back to putty:

add TOKEN with ID in docker-compose.yml

you can find docker-compose.yml

![find docker config](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/getconfig.JPG)

  

9. docker-compose.yml have to look like this in default

![config](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/Config.JPG)

  

10. Reboot Docker

![reboot](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/reboot.JPG)

11. Go on your TSD server VIA link connected to Telegram.

Go in preferences and connect to Telegram.

![linking](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/linkbot.JPG)

12. Push Test button after

RESULTS

![Results](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/Telegram/result.JPG)