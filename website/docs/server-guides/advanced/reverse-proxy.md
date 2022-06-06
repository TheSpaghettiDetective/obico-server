---
title: Configure Obico to work with a reverse proxy
---

:::danger
**Security Warning**: The guide below only cover the basic steps to set up a reverse proxy for self-hosted Obico Server. The setup required to properly secure your reverse proxy is too complicated to be covered here. Please do your own research to gather the necessary info before you proceed.
:::

You can set up a reverse proxy in front of your self-hosted Obico Server.

Two configuration items need to be set differently if you are using a reverse proxy.

## 1. "Domain name" in Django site configuration.

1. Open Django admin page at `http://tsd_server_ip:3334/admin/`.

2. Login with username `root@example.com`.

3. On Django admin page, click "Sites", and click the only entry "example.com" to bring up the site you need to configure. Set "Domain name" as follows:

Suppose:

* `reverse_proxy_ip`: The public IP address of your reverse proxy. If you use a domain name for the reverse proxy, this should the domain name.
* `reverse_proxy_port`: The port of your reverse proxy.

The "Domain name" needs to be set to `reverse_proxy_ip:reverse_proxy_port`. The `:reverse_proxy_port` part can be omitted if it is standard 80 or 443 port.

## 2. If the reverse proxy is accessed through HTTPS:

1. Open `docker-compose.yml`, find `SITE_USES_HTTPS: 'False'` and replace it with `SITE_USES_HTTPS: 'True'`.

2. Restart the server: `docker-compose restart`.

## NGINX

For webcam feed to work, remember to activate Websockets support. Otherwise there will no webfeed when accessing through proxy.

![NginxProxyManagerSettings](/img/server-guides/nginxsettings.png)

Please note that this is not a general guide. Your situation/configuration may be different.

* This configuration does a redirect from port 80 to 443.
* This config is IP agnostic meaning it should work for IPv4 or IPv6.
* This config supports HTTP/2 as well as HSTS TLSv1.3/TLSv1.2, please do note that anything relying on a websocket runs over http1.1.

```
server {
  listen 80;
  listen [::]:80;
  server_name YOUR.PUBLIC.DOMAIN.HERE.com;
  return 301 https://$host$request_uri;
}
server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  ssl_certificate /YOUR/PATH/HERE/fullchain.pem;
  ssl_certificate_key /YOUR/PATH/HERE/privkey.pem;
  ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
  ssl_prefer_server_ciphers on;
  ssl_stapling on;
  ssl_stapling_verify on;
  ssl_protocols TLSv1.3 TLSv1.2;
  ssl_early_data on;
  proxy_set_header Early-Data $ssl_early_data;
  ssl_dhparam /etc/ssl/certs/dhparam.pem;
  ssl_ecdh_curve secp384r1;
  ssl_session_cache shared:SSL:40m;
  ssl_session_timeout 4h;
  add_header Strict-Transport-Security "max-age=63072000;";
  server_name YOUR.PUBLIC.DOMAIN.HERE.com;
  access_log /var/log/tsd.access.log;
  error_log /var/log/tsd.error.log;
  location / {
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3334/;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_redirect off;
    client_max_body_size 10m;
  }
 location /ws/ {
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3334/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
  }
}
```

## Traefik

1. [Follow these instructions on how to setup Traefik (First two steps)](https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-debian-9)

1. `cd obico-server`

1. Edit the `docker-compose.override.yml` file with your favorite editor.

1. Add `labels:` and `networks:` to the `web:` section, and also add `networks:` at the end of the file:

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

1. Retart the Obico Server with `docker-compose restart`

1. You should now be able to browse to `spaghetti.your.domain`
