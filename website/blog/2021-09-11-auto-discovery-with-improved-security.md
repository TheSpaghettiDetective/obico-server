---
title: Auto-discovery re-implemented with improved security as strong as 2FA
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.obico.io/img/kj.jpg
tags: ['The Spaghetti Detective Updates']
---

I have [regained my confidence that The Spaghetti Detective app is on pretty solid ground when it comes to security](/blog/2021/09/11/security-incident-update). I take full responsibility for the blunder I made in the process of developing and deploying the auto-discovery feature. Meanwhile, we don't want to have the auto-discovery function disabled forever. It would be the easiest way moving forward, but also the laziest. We know auto-discovery has made it extremely easy for new users to link their printers to The Spaghetti Detective and everyone loved it! We still want to give them a way to do it, and do it securely.

And we found a way!

## The original auto-discovery design and implementation

<!-- truncate -->

To recap what caused the security vulnerability in the first implementation of auto-discovery: the security of it was based on 2 factors:

1. Public IP address. The OctoPrint that needs to be linked shares the same public IP address as the device that is being used to link it.
2. Timing. Auto-discovery would be active only for a limited period. The auto-discovery will be shut down once the printer is linked, or up to 1 hour print restarted. Based on our database records, 83% of the users get their printers linked within 3 minutes. That means all printers were in the discoverable state for under an hour, with 83% of them under 3 minutes.

According to the security expert who audited our code, the security vulnerability in this design wouldn't have been too bad if, *and only if,* everything was configured correctly. This is because, even if there are situations where an attacker can ["spoof the IP address"](https://www.kaspersky.com/resource-center/threats/ip-spoofing), or where multiple users [share the same public IP address](https://en.wikipedia.org/wiki/Carrier-grade_NAT), the chance for any printer to be caught discoverable "at the wrong time" was pretty low.

However, [I made a mistake by misconfiguring the load balancers](/blog/2021/08/19/what-happened-last-night#the-technical-details). This was what made the original security vulnerability 100x worse.

## The new auto-discovery with improved security as strong as 2FA

I have learned my lesson from that incident: **when it comes to security, there are no chances to be taken.**

So the TSD team set out to figure out a solution. And we ended up with something that is as strong as 2FA (2-Factor-Authentication).

Please bear with me here as I won't spare any details about the new auto-discovery design and implementation. I don't believe in "security by ambiguity". Instead, I want to present as much info to as many people as possible as I believe in Linus's law: *given enough eyeballs, all bugs are shallow.*

1. In auto-discovery, which is now up to only 10 minutes instead of 1 hour, The Spaghetti Detective plugin randomly generates a UUID as the `instance_id` and a 32-character `local_secret`.
1. The `instance_id`, along with the `private_ip`, are sent to The Spaghetti Detective server. The `local_secret`, however, is held in the memory and **never directly sent to The Spaghetti Detective server**. Instead, the `local_secret` can be retrieved only from a device on the local network by a direct connection to OctoPrint.
1. The device that is trying to link a printer will receive the `instance_id` and the `private_ip` from The Spaghetti Detective server, given its public IP address matches the one that OctoPrint uses to connect to the server.
1. The device then needs to initiate a direct, local network connection to OctoPrint running at the `private_ip`. It sends the `instance_id` in the request to "exchange for the local secret". If the device is not actually on the claimed public IP address, e.g., in case of an ip-spoofing attack, this connection will fail and hence prevents the attack.
1. The plugin will then confirm:
    - The connection actually comes from the local network. This means even if your OctoPrint has been exposed to the Internet (you probably shouldn't do that anyway) and hence subject to attack from outside of your local network, the request will be rejected anyway.
    - The `instance_id` matches the random UUID it previously generated.
    - The request doesn't come in outside the 10-minute auto-discovery window.
1. The plugin will return the `local_secret` to the requeter only if the checks above have passed.
1. Once the device received the `local_secret` from the plugin, it will send a "request to link" message to The Spaghetti Detective server.
1. The Spaghetti Detective server, after again verifying the public IP address of the "request to link" matches that of the OctoPrint in question, will forward the `local_secret` to the plugin for final verification.
1. The plugin receives the `local_secret` and verifies it matches the one being held in memory.
1. In addition, The Spaghetti Detective server enforces a very strict policy that **allows only 1 OctoPrint to be visible as auto-discovery at a time**. This restriction will prevent an attacker who can, in a sophisticated but rare situation, spoof the public IP of a victim, from even seeing the victim's printer.

Whew! That's all the steps we are taking to make sure auto-discovery is as secure as it can be. If any of the steps described above doesn't work as expected, the plugin will simply turn off auto-discovery. We know doing so will also prevent some legitimate users from using the auto-discovery feature and force them to fall back to [manual linking using the 6-digit code](/docs/user-guides/octoprint-plugin-setup-manual-link), which is less convenient. But again, we have learned that, under all circumstances, security triumphs over convenience.


## The bug bounty program!

After thorough auditing and testing, We believe with all these security measures combined will amount to a level of security compared to 2FA. We also know the evils can be in the implementation details. Therefore we are launching a bug bounty program for all the code involved in the auto-discovery so that we can get enough "eyeballs on the code".

Please dive into the code, peel behind the scene, and [report to us](mailto:support@thespaghettidetective.com) if you find any vulnerability. Once confirmed, we will be happy to award you 500 DHs or 1 year of free Pro subscription!

- In the plugin
    - [https://github.com/TheSpaghettiDetective/OctoPrint-TheSpaghettiDetective/blob/master/octoprint_thespaghettidetective/printer_discovery.py](https://github.com/TheSpaghettiDetective/OctoPrint-TheSpaghettiDetective/blob/master/octoprint_thespaghettidetective/printer_discovery.py).
- In the server
    - [https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/blob/master/web/api/printer_discovery.py](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/blob/master/web/api/printer_discovery.py)
    - [https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/blob/master/web/api/viewsets.py#L411](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/blob/master/web/api/viewsets.py#L411)

