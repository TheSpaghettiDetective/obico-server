---
id: pushover-notification-plugin
title: Build a Pushover notification plugin for Obico
---

This tutorial walks you through the steps to build a Pushover notification plugin and run it in your self-hosted Obico server. As a matter of fact, the Pushover notification that's shipped with the Obico server is just a slightly polished version.

## 1. Create a Pushover app and obtain its API Token

Creating a Pushover app is a surprisingly simple process. Follow [the Pushover instructions](https://pushover.net/api#registration).

If everything goes smoothly, you should see a page similar to this when you are done:

![](/img/tutorials/pushover-app-token.jpg)

The "API Token/Key" will be used to configure the Obico notification plugin we will create in this tutorial.


## 2. Create a Obico notification plugin

### 2.1 Backend plugin files

1. Create a sub-folder named `mypushover` in `backend/notifications/plugins`. The folder name `mypushover` is your plugin ID and shouldn't be the same as any other plugins `backend/notifications/plugins`.
2. Download [this file](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/backend/notifications/plugins/pushover/__init__.py) and save it as `__init__.py` in `backend/notifications/plugins/mypushover`.

### 2.2 Frontend plugin files

1. Download [this file](https://raw.githubusercontent.com/TheSpaghettiDetective/TheSpaghettiDetective/master/frontend/src/notifications/plugins/pushover.vue) and save it as `mypushover.vue` in `frontend/src/notifications/plugins/`. Please note that the file name `mypushover.vue` should match the plugin ID you chose in step 2.1.
2. Open the file `frontend/src/notifications/plugins.js` and add the following lines to the bottom of the file:
```
...
  mypushover: {
    displayName: 'My Pushover plugin',
  },
...
```

### 2.3 Configure environment variables

1. Make a copy of `dotenv.example` and rename the copy as `.env` in the project root directory if you haven't previously done so.
2. Open the `.env` file.
3. Add a line that looks like this:
```
...
PUSHOVER_APP_TOKEN="the-pushover-app-token-you-obtained-in-step-1"
...
```

### 2.4. Rebuild the frontend

Run these command to rebuild the frontend:

```
cd frontend
yarn
yarn build
cd ..
```

## 3. Restart the server

```
docker-compose restart
```

You should be able to see the notification plugin you just created on your Obico server and start receiving notifications from your own pushover app!

![](/img/tutorials/pushover-notification-plugin-done.jpg)

