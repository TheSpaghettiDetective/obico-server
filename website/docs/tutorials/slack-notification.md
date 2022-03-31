---
sidebar_position: 0
id: slack-notification
title: Build a Slack notification plugin for Obico
---

This tutorial walks you through the steps to build a slack notification and run it in your self-hosted Obico server. As a matter of fact, the slack notification that's shipped with the Obico server is just a slightly polished version.

## 1. Create, configured, and distribute a Slack app

In order to send messages to Slack using its APIs, you will need to create a Slack app first.

### 1.1. Create a Slack app

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps).
1. Click the **Create New App** button. Select **From scratch** from the options.
1. Give your app a name and the Slack workspace the app will be registered in.

### 1.2. Configure the Slack app

1. Choose **OAuth & Permissions** from the menu list on the left.
1. In the **Scopes** section, under **Bot Token Scopes** (*NOT User Token Scopes*), add the following scopes:
    - `chat:write`
    - `chat:write.public`
    - `channels:read`
    - `groups:read`
1. Now you need to add a redirect URL to the **Redirect URLs** section. The redirect URL should be the URL your self-hosted Obico server can be accessed on from the Internet (so that Slack can reach it) via HTTPS. Refer to the [Server Configuration Guide](#) for how this can be set up.

### 1.2. Distribute the Slack app

1. On the Slack app page, select **Basic Information** from the menu list on the left.
1. Click **Manage distribution**, then **Distribute App**.
1. On the next page, click **Activate Public Distribution**.
1. Select **Basic Information** from the menu list on the left.
1. Find the **Client ID** and **Client Secret** on that page. You will need it to configure the Obico server.

