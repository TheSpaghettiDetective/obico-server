# TheSpaghettiDetective

This repo is everything you need to run a server for [The Spaghetti Detective](https://thespaghettidetective.com), the coolest, AI-based solution for 3D printer remote management and monitoring.

The core of this project is based on a Deep Learning model. [See how the model works on real data](https://app.thespaghettidetective.com/publictimelapses/).

# Install and run the server

If you are on Windows 10 and prefer a video tutorial, head to LukesLaboratory's [awesome video](https://www.youtube.com/watch?v=8l4C_K9S2-Y) (Big shout-out to [@LukesLaboratory](https://twitter.com/LukesLaboratory/)).

If you otherwise prefer textual instructions, follow the steps below.

## Prerequisites

The Spaghetti Detective server needs to run on a real computer (Not a Pi, unfortunately. Rapberry Pi, or Latte Panda, is just not powerful enough to run the Machine Learning model). On that server, make sure
the following softwares are installed:

- Docker and Docker-compose. But you don't have to understand how Docker or Docker-compose works.
    - Install Docker ([Windows](https://docs.docker.com/docker-for-windows/install/), [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Mac](https://docs.docker.com/docker-for-mac/install/)). **Important:** If your server has an old Docker version, please follow the instructions in these links to upgrade to the latest version, otherwise you may run into all kinds of weird problems.
    - [Install Docker-compose](https://docs.docker.com/compose/install/). You need Docker-compose 1.21.0 or higher version.
    - (**Windows only**) Make sure "Shared Dirves" is checked in Docker settings
<img src="https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/shared_drives.png" width="409" height="200"></img>

- git ([how to install](https://git-scm.com/downloads)).

You will also need an email account that has SMTP access enabled. For a gmail account, this is [how you enable SMTP access](https://support.google.com/accounts/answer/6010255?hl=en). Other web mail such as Yahoo
should also work but we haven't tried them.

## Get the code and start the server.

1. Get the code:

```
git clone https://github.com/TheSpaghettiDetective/TheSpaghettiDetective.git
```

2. Run it! Do **either** one of these based on what OS you are using:
    - If you are on Linux: `cd TheSpaghettiDetective && sudo docker-compose up -d`
    - If you are on Mac: `cd TheSpaghettiDetective && docker-compose up -d`
    - If you are on Windows: `cd TheSpaghettiDetective; docker-compose up -d`

3. Go grab a coffee. Step 2 would take up to 30 minutes. BTW, we need help to shorten this process. Let us know if you can pitch in.

4. There is no step 4. This is how easy it is to get The Spaghetti Detective up and running (thanks to Docker and Docker-compose).


# Basic server configuration

These are the bare minimum configuration required for the server to be functional.

## Obtain server's IP address

The Spaghetti Detective server needs to have an IP address that is accessible by OctoPrint. It can be an private IP address (192.168.x.y, etc) but there needs to be a route between OctoPrint and The Spaghetti Detective server.

## Port/Firewall

The Spaghetti Detective server listens on port 3334 (will be configurable in later version). Please make sure this port is not blocked from OctoPrint.

You can set up a reverse-proxy, such as nginx, in front of The Spaghetti Detective server, so that it's exposed on a different port. In this case, please use whichever port you choose to expose in the steps below. For simplicity
sake, this document assumes the server port is 3334.

## Login as Django admin

1. Open Django admin page at `http://your_server_ip:3334/admin/`

2. Login with username `root@example.com`, password `supersecret`. Once logged in, you can optionally (but highly encouraged to) change admin password using this link: `http://your_server_ip:3334/admin/app/user/1/password/`.

## Configure Django site

1. On Django admin page, click "Sites", and click the only entry "example.com" to bring up the site you need to configure. Change "Domain name" to `your_server_ip:3334`. No "http://", "https://" prefix or trailing "/", otherwise it will NOT work.

2. Click "Save". Yes it's correct that Django is not as smart as most people think. ;)

![Site configuration](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/site_config.png)

## Configure Email server (SMTP)

The following is using gmail as an example. Other web mail services may vary slightly, such as EMAIL_PORT

1. In `TheSpaghettiDetective` directory, find and open `docker-compose.yml` using your favorite editor.

2. Find the following lines, and set them to the correct values of your email account:

```
      EMAIL_HOST:     # -> such as smtp.gmail.com
      EMAIL_HOST_USER:   # -> such as your email address for a Gmail account
      EMAIL_HOST_PASSWORD:    # -> your email account password
      EMAIL_PORT: 587
      EMAIL_USE_TLS: 'True'
```

# Done!

That's it! You now have a fully-functional The Spaghetti Detective server that your OctoPrint can talk to. We hope setting up the server has not been overwhelming.

# Configure The Spagetti Detective OctoPrint Plugin to use your own server

Before you can configure The Spagetti Detective OctoPrint Plugin to use your own server, you need add a printer to The Spagetti Detective server you just built and obtain the secret token for that. To do so:

1. Pointing your browser to `http://your_server_ip:3334/`.

1. Log in as a user (you can just login with `root@example.com` but it's more secure to use a non-admin user). Add a new printer as described in [this guide](https://www.thespaghettidetective.com/docs/octoprint-setup.html#step-1-sign-up-the-spaghetti-detective-beta-account) and obtain the secret token.

Then, on The Spaghetti Detective plugin settings page:

1. Check the box "I have my own TSD server. Don't check this unless you know what you are doing."

2. Enter `http://your_serer_ip:3334/`. This time you need to enter both "http://" and the trailing "/". I know it's confusing but...

3. Enter the secret token you copied from the previous step.

4. Click "Save". OctoPrint isn't necessarily smarter than Django after all.

![Site configuration](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/docs/plugin_config.png)


# Advanced server configuraion

## Enable social login (TBD)

## Change email server to be one other than `sendmail` on localhost (TBD)


# Operating and maintaining The Spaghetti Detective server

## Upgrade server

    git pull
    sudo docker-compose up --build -d

## Backup database

Just make a copy of `TheSpaghettiDetective/web/db.sqlite`

# How to train your own Machine Learning model (TBD)

# Difficulties at getting The Spaghetti Detective server up and running?

Check the [FAQ document](docs/faq.md). If you can't find the answer there, [open an issue](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/new).
