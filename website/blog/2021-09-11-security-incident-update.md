---
title: An update on the 8/19 security incident
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.obico.io/img/kj.jpg
tags: ['The Spaghetti Detective Updates']
---

The Spaghetti Detective had [a serious security incident](/blog/2021/08/19/what-happened-last-night) on August 19th. That incident was caused by a mistake I made in the function called "auto-discovery".

This post is to provide an update on what we have done after the incident.

## What we did on the day of the incident:

* Immediately disabled auto-discovery once we found out the vulnerability, about 4.5 hours after it happened.
* Identified and deactivated the 73 printers that were exposed to this vulnerability during those 4.5 hours.
* Sent an email to all The Spaghetti Detective users to disclose this incident.
* Offered all Pro subscribers the option to cancel the subscription and receive a full refund.

## What we have done afterward:

* Had the code base of The Spaghetti Detective app thoroughly audited by a Security Consultant. **No other vulnerability is identified.**
* Performed vulnerability deep scans using Detectify, which distributed "exploitation scanning" to 30 whitehat hackers. **Again nothing showed up.**
* Designed, implemented, audited, and thoroughly tested a new way to do auto-discovery. To "have more eyeballs on the code", [we have launched a bug bounty program](/blog/2021/09/11/auto-discovery-with-improved-security).

We have regained the confidence that The Spaghetti Detective app remains on a pretty solid ground when it comes to security. Meanwhile, we have learned not to take things for granted. We will keep our antenna up for any signs of vulnerability or abuse.

## *A personal note from Kenneth:*

*I was waiting for a shitstorm after I sent the email about the security incident to all The Spaghetti Detective users. The consequence of the incident was serious. Although only 73 users were impacted, it resulted in unauthorized access for at least one user's printer. I didn't expect this kind of blunder to be easily forgiven.*

*Instead, I was humbled by the kindness and support in the overwhelming responses you folks sent to me. I only did what I should have done: taking responsibility for my own mistake and cleaning up the mess. But you generously showered me with so much love!*

*At that moment, I felt lucky. Not because I escaped a shitstorm. I felt lucky because I realized I happened to be serving the most awesome group of people in the world. I started The Spaghetti Detective to give all 3D printing enthusiasts a way to securely and safely monitor your printers. I have disappointed you once. The only thing I can do is to make The Spaghetti Detective better and safer so that I won't disappoint you again!*

<div><em>- Kenneth</em></div>

<div><em>Lead Developer @ The Spaghetti Detective</em></div>
