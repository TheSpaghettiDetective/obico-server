# Advanced server configuration

## Using a reverse proxy

We are using the reverse proxy traefik.

 1. [Follow these instructions on how to setup Traefik (First two steps)](https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-debian-9)
 2. Navigate to your directory of TheSpaghettiDetective `cd TheSpaghettiDetective`
 3. Edit the docker-compose.yml file with your favorite editor: `nano docker-compose.yml`
 4. - Add `labels:` and `networks:` to the `web:` section
    - and also add `networks:` at the end of the file
    ```
    ...
      web:
        <<: *web-defaults
        hostname: web
        ports:
          - 3334:3334
        labels:
          - traefik.backend=thespaghettidetective
          - traefik.frontend.rule=Host:spaghetti.your.domain
          - traefik.docker.network=web
          - traefik.port=3334
        networks:
          - web
        depends_on:
          - ml_api
        command: sh -c "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:3334"

      ...

      ...

        networks:
          web:
            external: true
      ```
 5. Start TheSpaghettiDetective with `docker-compose up -d`
 6. You should now be able to browse to `spaghetti.your.domain`

## Enable telegram notifications

1. Create a bot. You can do this by messaging [@BotFather](https://t.me/botfather) - see [telegram's documentation](https://core.telegram.org/bots#3-how-do-i-create-a-bot) for further information.
2. Add TELEGRAM_BOT_TOKEN to docker-compose.yml with the token @BotFather generated.
3. Set the bot's domain by messaging @BotFather `/setdomain`, selecting your bot, and sending him your bot's domain name. This must be a publicly-accessible domain name. You can temporarily generate a publicly-accessible domain name through a local tunnel - see [https://localtunnel.github.io/www/] or [https://serveo.net/#manual] for two good options.
4. Log in to telegram from your user preferences page (let's say your publicly accessible domain name is `https://tunnel.serveo.net/`. You'd go to `https://tunnel.serveo.net`, log into your local TheSpaghettiDetective account -- by default `root@example.com` -- and go to the user preferences page, then log into telegram and hit the form's `save` button).
5. That's it! Once you've logged in once, you will no longer need a publicly-accessible domain name.

## Enable social login (TBD)

## Change email server to be one other than `sendmail` on localhost (TBD)
