If you wish to utilize Nginx as a reverse proxy to sit in front of your TSD server please use the below configuration as a guide.<br>
Please note that this is a guide and every situation/configuration is different. <br>
This configuration does a redirect from port 80 to 443.<br>
This config is IP agnostic meaning it should work for IPv4 or IPv6.<br>
This config supports HTTP/2 as well as HSTS TLSv1.3/TLSv1.2, please do note that anything relying on a websocket runs over http1.1.<br>

server {<br>
  listen 80;<br>
  listen [::]:80;<br>
  server_name YOUR.PUBLIC.DOMAIN.HERE.com;<br>
  return 301 https://$host$request_uri;<br>
}<br>
server {<br>
  listen 443 ssl http2;<br>
  listen [::]:443 ssl http2;<br>
  ssl_certificate /YOUR/PATH/HERE/fullchain.pem;<br>
  ssl_certificate_key /YOUR/PATH/HERE/privkey.pem;<br>
  ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;<br>
  ssl_prefer_server_ciphers on;<br>
  ssl_stapling on;<br>
  ssl_stapling_verify on;<br>
  ssl_protocols TLSv1.3 TLSv1.2;<br>
  ssl_early_data on;<br>
  proxy_set_header Early-Data $ssl_early_data;<br>
  ssl_dhparam /etc/ssl/certs/dhparam.pem;<br>
  ssl_ecdh_curve secp384r1;<br>
  ssl_session_cache shared:SSL:40m;<br>
  ssl_session_timeout 4h;<br>
  add_header Strict-Transport-Security "max-age=63072000;";<br>
  server_name tsd.playtfg.com;<br>
  access_log /var/log/tsd.access.log;<br>
  error_log /var/log/tsd.error.log;<br>
  location / {<br>
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3334/;<br>
    proxy_set_header X-Real-IP $remote_addr;<br>
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;<br>
    proxy_set_header Host $http_host;<br>
    proxy_set_header X-Forwarded-Proto https;<br>
    proxy_redirect off;<br>
    client_max_body_size 10m;<br>
  }<br>
 location /ml_api/ {<br>
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3333/;<br>
    proxy_set_header X-Real-IP $remote_addr;<br>
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;<br>
    proxy_set_header Host $http_host;<br>
    proxy_set_header X-Forwarded-Proto https;<br>
    proxy_redirect off;<br>
    client_max_body_size 10m;<br>
  }<br>
 location /ws/web/ {<br>
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3334/ws/web/;<br>
    proxy_http_version 1.1;<br>
    proxy_set_header Upgrade $http_upgrade;<br>
    proxy_set_header Connection "Upgrade";<br>
  }<br>
 location /ws/janus/ {<br>
    proxy_pass http://YOUR BACKEND IP/HOSTNAME:3334/ws/janus/;<br>
    proxy_http_version 1.1;<br>
    proxy_set_header Upgrade $http_upgrade;<br>
    proxy_set_header Connection "Upgrade";<br>
  }<br>
<br>
}<br>
