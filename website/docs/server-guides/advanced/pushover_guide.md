---
title: Pushover Notifications Setup Guide
---

:::note
This is a community-contributed guide. This guide is based on certain Obico community members' own setup and hence may not work for you.
:::

This tutorial walks you through the steps to configure Pushover notifications on your self-hosted Obico Server.

## 1. Create a Pushover app and obtain its API Token and your User Key {#1-create-a-pushover-app-and-obtain-its-api-token-and-your-user-key}

Creating a Pushover app is a surprisingly simple process. Follow [the Pushover instructions](https://pushover.net/api#registration).

If everything goes smoothly, you should see a page similar to this when you are done with your new **API key**:

![](/img/server-guides/pushover/pushover-app-token.jpg)

While you are on Pushover's site, make note of your **User Key** as well. It should be displayed on the Pushover homepage if you are logged into your account.

![](/img/server-guides/pushover/pushover-user-key.jpg)

### 2 Configure environment variables {#2-configure-environment-variables}

1. Make a copy of `dotenv.example` and rename the copy as `.env` in the project root directory if you haven't previously done so.
2. Open the `.env` file.
3. Uncomment the line with `PUSHOVER_APP_TOKEN` and paste in your API key obtained in step 1 like this:
```
...
PUSHOVER_APP_TOKEN=the-pushover-app-token-you-obtained-in-step-1
...
```

### 3. Rebuild the app containers {#3-rebuild-the-app-containers}

Run this command to rebuild your app containers:

```bash
docker-compose up --build -d
```

## 4. Configure your User key and notification preferences {#4-configure-your-user-key-and-notification-preferences}

1. Navigate to the *Preferences* panel in the web UI.
2. Click the **Pushover** option under *Notifications*
3. Paste in your Pushover User Key obtained in step 1
4. Ensure the **Enable notification** box is checked. Also check/uncheck your preferred notification events

![](/img/server-guides/pushover/pushover-notification-configurations.jpg)
