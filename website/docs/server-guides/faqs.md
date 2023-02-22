---
title: FAQs
---

## Why doesn't the webcam streaming work for my self-hosted server? {#why-doesnt-the-webcam-streaming-work-for-my-self-hosted-server}

1. Switch to using [the Obico Cloud](https://app.obico.io/) to see if the streaming starts to work now. If it doesn't, go through [the webcam streaming troubleshooting guide for the Obico Cloud](/docs/user-guides/webcam-feed-is-not-showing/).

:::tip

Because all the Pro features for the Obico Cloud are also available for the self-hosted servers, self-hosted servers are eligible for [the Premium Streaming](/docs/user-guides/webcam-streaming-for-human-eyes/).

:::

2. If the streaming works in the Obico Cloud, but not in your self-hosted server, the problem is with how you set up the self-hosted server.

3. Does the Basic Streaming work? Start a test print. If the webcam streaming starts to show up, the Basic Streaming works.

4. If the Basic Streaming doesn't work, go [checkout the plugin log file](/docs/user-guides/turn-on-debug-logging/) to see if there are any errors.

5. If the Basic Streaming works, but the Premium Streaming doesn't, go checkout [why the Premium Streaming doesn't work](#why-doesnt-the-premium-streaming-work)

## Why doesn't the Premium Streaming work? {#why-doesnt-the-premium-streaming-work}

The Premium Streaming is based on [the WebRTC protocol](https://webrtc.org/). WebRTC is an interesting network protocol that is very susceptible to network configurations.

If you are not getting the Premium Streaming in your self-hosted server, the first step is to link your printer to [the Obico Cloud](https://app.obico.io) and test it there (your first month on the Obico Cloud is a free trial of Premium Streaming. No credit card required.). If the streaming doesn't work in the cloud, you need to follow [this troubleshooting guide](/docs/user-guides/webcam-feed-is-not-showing/) to figure it out.

If the Premium Streaming works in the Obico Cloud but not in your self-hosted server, chances are there are some problems with your server's network configurations.

At the minimum, your server's firewall should have the following rules allowed:

- Inbound - port 3334 or whatever port your reverse proxy is on. If your server is on http.
- If you are using a reverse proxy, make sure it proxies WebSocket protocol.
- Outbound - stun.l.google.com:19302.
- UDP port 3478.
- UDP port 5349.
- UDP port range 20000-24999.

But having all these firewall rules in place still doesn't guarantee the Premium Streaming. If you feel adventurous, Google "WebRTC network configuration requirements" for more details.

## I got an HTTP 500 error when I do "Sent test email". Why? {#i-got-an-http-500-error-when-i-do-sent-test-email-why}

More likely than not, it's because your email configurations are set incorrectly.

Check out [this help guide](/docs/server-guides/configure/#email-smtp) for how you can configure email (SMTP) for the Obico Server. There are also a few things you can do to troubleshoot:

1. Run `docker compose exec web env | grep EMAIL` to confirm the email configurations have been correctly picked up by the Obico Server.
1. Run `docker compose logs -f web` when you press the "Sent test email" button and look for the specific error messages.
