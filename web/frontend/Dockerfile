FROM node:12.16.3

ARG uid
ARG gid
ARG user=frontdev
ARG group=frontdev

RUN groupadd -o -g $gid $group && useradd -o -g $gid -u $uid $user && \
    mkdir -p /home/$user && chown -R $user:$group /home/$user

RUN mkdir /code && mkdir /code/node_modules 

RUN chown -R $user:$group /code

WORKDIR /code

USER $user
