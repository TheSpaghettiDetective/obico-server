---
id: webcam-feed-is-not-showing
title: Troubleshoot webcam streaming issues
---

In most cases, Obico will automatically figure out how to stream the webcam to the Obico app, such as the resolution, framerate, the bandwidth requirements, etc. However, in case you run into webcam streaming issues, follow this troubleshooting guide to solve the issues.

The first step is to check which webcam streaming issue you are experiencing:

import TOCInline from '@theme/TOCInline';

<TOCInline toc={toc} />

## Webcam only refreshes once about every 10 seconds (0.1FPS webcam stream)

The most common cause for this problem is that [Janus is not installed on your printer or SBC](/docs/user-guides/webcam-install-janus/). When this is the case, you will also see a warning in the Obico app:

![Janus Not Found](/img/user-guides/helpdocs/janus-not-found-warning.png)

The solution is to install Janus on your printer or SBC. [Follow this guide for details](/docs/user-guides/webcam-install-janus/).

If you are running a self-hosted Obico server, it's also possible that Janus is installed but the WebRTC connection can't be established due to your network configurations (firewall, routing, NAT configuration in your router, etc). To check if this is the case, [re-link your printer to the Obico cloud](/docs/user-guides/relink-printer/). If the issue is gone, the problem is with the settings of your server or its network configuration.

Follow [this guide](/docs/user-guides/webcam-stream-stuck-at-1-10-fps/) for other less common problems that may cause the webcam to stream at only 0.1FPS.

## Webcam stream is choppy

The most common reason why your webcam stream appears choppy is because you don't have an Obico Pro subscription.

* You are eligible for the Premium Streaming (25 frames-per-second) if you are currently a Pro plan subscriber or in the free 1-month Pro trial.
* You are eligible for only the Basic Streaming if you are on the Free plan. In this case, the webcam stream is up to 5 frames-per-second, which can appear to be quite choppy. Also it's throttled for 30 seconds every minutes.

Visit [your Obico account subscription page](https://app.obico.io/user_preferences/subscription/) if you are not sure.

:::info
Learn more about [Premium Streaming vs Basic Streaming](/docs/user-guides/webcam-streaming-for-human-eyes).
:::

If you already have a Pro subscription but your webcam stream is still choppy, follow [this complete troubleshooting guide](/docs/user-guides/webcam-feed-is-laggy/).

## No webcam in the Obico app

:::tip
After you open the Obico mobile app or web app, wait for up to 5 seconds for the webcam stream to load.
:::

By default, Obico will automatically stream the webcam(s) configured in Klipper (Mainsail/Fluidd) or OctoPrint. If there is no webcam stream in the Obico app, check if the webcam stream works correctly in Klipper (Mainsail/Fluidd) or OctoPrint.

If the webcam stream works in Klipper (Mainsail/Fluidd) or OctoPrint, but is missing or a black screen in the Obico app, you may have to manually configure webcam(s) in Obico.

- [Configure webcam in Obico for Klipper](/docs/user-guides/moonraker-obico/webcam/)
- [Configure webcam in Obico for OctoPrint](/docs/user-guides/multiple-cameras-octoprint/)

If you are sure the webcam is configured correctly in Obico, you can set the logging level to verbose to check for errors. Here is how you can [do it in Obico for Klipper](/docs/user-guides/moonraker-obico/logging-file/) or [in Obico for OctoPrint](/docs/user-guides/turn-on-debug-logging/). Look for log messages similar to:

```
2024-09-01 11:42:19,461     ERROR  backoff - Giving up capture_jpeg(...) after 3 tries (urllib.error.HTTPError: HTTP Error 502: Bad Gateway)
2024-09-01 11:42:19,462     ERROR  obico.webcam_stream - Failed to connect to webcam to retrieve resolution. Using default.
Traceback (most recent call last):
  File "/home/pi/moonraker-obico.ssh/moonraker_obico/webcam_stream.py", line 59, in get_webcam_resolution
    (_, img_w, img_h) = get_image_info(capture_jpeg(webcam_config, force_stream_url=True))
  File "/home/pi/.local/lib/python3.9/site-packages/backoff/_sync.py", line 94, in retry
    ret = target(*args, **kwargs)
  File "/home/pi/.local/lib/python3.9/site-packages/backoff/_sync.py", line 43, in retry
    ret = target(*args, **kwargs)
  File "/home/pi/moonraker-obico.ssh/moonraker_obico/webcam_capture.py", line 51, in capture_jpeg
    with closing(urlopen(stream_url)) as res:
  File "/usr/lib/python3.9/urllib/request.py", line 214, in urlopen
    return opener.open(url, data, timeout)
  File "/usr/lib/python3.9/urllib/request.py", line 523, in open
    response = meth(req, response)
  File "/usr/lib/python3.9/urllib/request.py", line 632, in http_response
    response = self.parent.error(
  File "/usr/lib/python3.9/urllib/request.py", line 561, in error
    return self._call_chain(*args)
  File "/usr/lib/python3.9/urllib/request.py", line 494, in _call_chain
    result = func(*args)
  File "/usr/lib/python3.9/urllib/request.py", line 641, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 502: Bad Gateway
```

If you see errors that seem to be related to webcam streaming, but you can't figure out what's causing them, [get help from a human](/docs/user-guides/contact-us-for-support).


## Get help from a human  {#6-if-none-of-the-above-worked}

If your issue is not listed above, or you have exhausted the troubleshooting guide but still can't get the issue resolved, [get help from a human](/docs/user-guides/contact-us-for-support).
