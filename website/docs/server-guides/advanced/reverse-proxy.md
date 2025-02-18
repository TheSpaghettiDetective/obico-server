---
title: Configure Obico to work with a reverse proxy
description: Learn how to configure Obico to work with a reverse proxy.
---

:::danger
**Security Warning**: The guide below only cover the basic steps to set up a reverse proxy for self-hosted Obico Server. The setup required to properly secure your private network is too complicated to be covered here. Please do your own research to gather the necessary info before you proceed.
:::

:::note
This is a community-contributed guide. This guide is based on certain Obico community members' own setup and hence may not work for you.
:::

:::tip
Some Obico community members have found it easier to set up NGINX reverse proxy using NGINX Proxy Manager. You can try your luck by following [this community-contributed guide](nginx-proxy-manager.md).
:::

You can set up a reverse proxy in front of your self-hosted Obico Server.

Two configuration items need to be set differently if you are using a reverse proxy.

## 1. "Domain name" in Django site configuration. {#1-domain-name-in-django-site-configuration}

1. Open Django admin page at `http://tsd_server_ip:3334/admin/`.

2. Login with username `root@example.com`.

3. On Django admin page, click "Sites", and click the only entry "example.com" to bring up the site you need to configure. Set "Domain name" as follows:

Suppose:

* `reverse_proxy_ip`: The public IP address of your reverse proxy. If you use a domain name for the reverse proxy (e.g. `reverse_proxy_domain`), this should the domain name.
* `reverse_proxy_port`: The port of your reverse proxy.

The "Domain name" needs to be set to `reverse_proxy_ip:reverse_proxy_port`. The `:reverse_proxy_port` part can be omitted if it is standard 80 or 443 port.

## 2. If the reverse proxy is accessed through HTTPS: {#2-if-the-reverse-proxy-is-accessed-through-https}

1. If you haven't already, make a copy of `dotenv.example` and rename it as `.env` in the `obico-server` directory.
2. Open `.env` using your favorite editor.
3. Find `SITE_USES_HTTPS=False` and replace it with `SITE_USES_HTTPS=True`.
4. Restart the server: `docker-compose restart`.

## 3. If an CSRF verification failed error (403 forbidden) occurs: {#3-if-an-csrf-verification-failed-error-403-forbidden-occurs}

1. If you haven't already, make a copy of `dotenv.example` and rename it as `.env` in the `obico-server` directory.
2. Open `.env` using your favorite editor.
3. Find `CSRF_TRUSTED_ORIGINS=` and replace it with `CSRF_TRUSTED_ORIGINS=["reverse_proxy_domain"]`.
4. Restart the server: `docker-compose restart`.

## NGINX {#nginx}

For webcam feed to work, remember to activate Websockets Support. Otherwise there will no webfeed when accessing through proxy.

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

## Traefik {#traefik}

1. [Follow these instructions on how to setup Traefik (First two steps)](https://www.digitalocean.com/community/tutorials/how-to-use-traefik-as-a-reverse-proxy-for-docker-containers-on-debian-9)

1. `cd obico-server`

1. Edit the `docker-compose.override.yml` file with your favorite editor.

1. Add `labels:` and `networks:` to the `web:` section, and also add `networks:` at the end of the file:

    ```yaml
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

1. Restart the Obico Server with `docker compose restart`

1. You should now be able to browse to `spaghetti.your.domain`


## IIS {#IIS}

:::warning

This is a community-contributed guide. And this guide involves editing the source code of Obico. This may not be suitable for everyone.
:::

IIS & Windows can also reverse proxy to Obico. See the below example `web.config` definition using `obico.mydomain.com` as the external address and `192.168.1.100:3334` as the internal address; replace with the appropriate values.

```
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule1" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://192.168.1.100:3334/{R:1}" />
                    <serverVariables>
                        <set name="HTTP_X_ORIGINAL_ACCEPT_ENCODING" value="{HTTP_ACCEPT_ENCODING}" />
                        <set name="HTTP_ACCEPT_ENCODING" value="" />
                        <set name="HTTP_SEC_WEBSOCKET_EXTENSIONS" value="0" />
                    </serverVariables>
                </rule>
            </rules>
            <outboundRules>
                <rule name="ReverseProxyOutboundRule1" preCondition="ResponseIsHtml1">
                    <match filterByTags="A, Form, Img" pattern="^http(s)?://192.168.1.100:3334/(.*)" />
                    <action type="Rewrite" value="http{R:1}://obico.mydomain.com/{R:2}" />
                </rule>
                <rule name="RestoreAcceptEncoding" preCondition="NeedsRestoringAcceptEncoding">
                    <match serverVariable="HTTP_ACCEPT_ENCODING" pattern="^(.*)" />
                    <action type="Rewrite" value="{HTTP_X_ORIGINAL_ACCEPT_ENCODING}" />
                </rule>
                <preConditions>
                    <preCondition name="ResponseIsHtml1">
                        <add input="{RESPONSE_CONTENT_TYPE}" pattern="^text/html" />
                    </preCondition>
                     <preCondition name="NeedsRestoringAcceptEncoding">
                        <add input="{HTTP_X_ORIGINAL_ACCEPT_ENCODING}" pattern=".+" />
                    </preCondition>
                </preConditions>
            </outboundRules>
        </rewrite>
    </system.webServer>
</configuration>
```
You will also need to edit your `applicationHost.config` file (default location of \Windows\System32\inetsrv\config) to allow IIS to edit the necessary headers. Replace `Obico reverse proxy` with your IIS site name defintion.
```
     <location path="Obico reverse proxy">
        <system.webServer>
            <rewrite>
                <allowedServerVariables>
                    <add name="HTTP_ACCEPT_ENCODING" />
                    <add name="HTTP_X_ORIGINAL_ACCEPT_ENCODING" />
                    <add name="HTTP_SEC_WEBSOCKET_EXTENSIONS" />
                </allowedServerVariables>
            </rewrite>
        </system.webServer>
    </location>
```
Finally, on your Obico server, you will need to specify the fully qualified domain name for which you want Obico to issue cookies. There is likely some mechanism to make this work automatically (as Obico/Django should be able to detect the domain under which it is being accessed and refer to that value) but it is possible that the above IIS proxy configuration is not relaying the necessary informaiton for it to do that. A workaround is to manually specify the FQDN in `/backend/config/settings.py`. Add these two lines in the `SESSION_COOKIE` section near the beginning of the file, replacing `obico.mydomain.com` with your FQDN:
```
SESSION_COOKIE_DOMAIN = "obico.mydomain.com"
CSRF_COOKIE_DOMAIN = "obico.mydomain.com"
```