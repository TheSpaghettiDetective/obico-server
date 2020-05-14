FROM node:12.16.3

ARG uid
ARG gid
ARG user=frontdev
ARG group=frontdev

RUN groupadd -o -g $gid $group && useradd -o -g $gid -u $uid $user && \
    mkdir -p /home/$user && chown -R $user:$group /home/$user

RUN mkdir -p /app/frontend && mkdir /app/node_modules && mkdir -p /app/static_build

RUN chown -R $user:$group /app

WORKDIR /app/frontend/

VOLUME /app
VOLUME /app/static_build

USER $user
