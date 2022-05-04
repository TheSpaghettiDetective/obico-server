---
title: A detailed analysis of the security incident last night
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
tags: ['The Spaghetti Detective Updates']
---

I screwed up. It was the first security breach The Spaghetti Detective has had in 2 years of her existence. But it was an embarrassing one that I can't forgive myself for.

## What happened?

I made a stupid mistake last night when I re-configured TSD cloud to make it more efficient and run faster. My mistake created a security vulnerability for about 8 hours. The users who happened to be linking a printer at that time were able to see each other's printer through auto-discovery, and were able to link to them too! We were notified of [a case in which a user started a print on someone else's printer](https://www.reddit.com/r/3Dprinting/comments/p7jdhi/wake_up_this_morning_and_see_this_on_my_3d/).

73 users got impacted as a result. It's not a huge number. There are bugs that impact a lot more users. But the consequence is very severe. Nobody wants his/her own printers being linked to and controlled by another account.

I created The Spaghetti Detective to let all 3D printing hobbyists have a way to safely monitor their printers from everywhere. And this is one of the worst mistakes I can make. My sincere apologies to our community for this horrible mistake.

<!-- truncate -->

## The technical details

One of the ways users can link their printers to their TSD accounts is through "auto-discovery". Auto-discovery is based on the fact that when devices on the same local network try to connect to the Internet, they will have the same public IP address. Hence the TSD server can match the Raspberry Pi with the computer/phone that is located in the same local network to let them discover each other.

Last night, when I went through the [load-balancer](https://www.nginx.com/resources/glossary/load-balancing/) reconfiguration, I made a mistake by missing a configuration to let the load balancer pass the public IP address of the connecting client to the backend TSD server. Instead, the load-balancer would just pass its own IP address to the server.

As a result, the server got the same IP address for the users who happened to be connecting their printer to TSD at the same time. The server thought they were on the same local network, and hence allowed them to link each other's printer!

## The scope of the impact and what we did to fix it

Our database shows that during the period of the incident, 73 users tried to link their printers to their TSD accounts. It was highly unlikely they were all trying to link at exactly the same time, but out of abundant precautions, we took the following measures:

1. Turned off the auto-discovery function as soon as we found this security vulnerability and hence prevented this problem from impacting more users.
1. Disabled the secure token for all printers that belonged to these 73 impacted users. Once a token is disabled, TSD plugin will refuse to trust the server and hence can no longer be remotely controlled. Only the people who have physical access to that printer can do so.
1. Send emails to all these 73 users to inform them about what happened, and the ways to get their printer back.

Users who were not linking during this period were not impacted. No user data, login credentials, or any other data were breached.

## FAQs

#### Is my TSD account affected? If so, what should I do about it?

If you were one of 73 users who got affected, you would have received a separate email from us.

If you were one of the affected users, we have disabled your printer token so it can't be connected remotely. You will need to [re-link your printer](https://www.thespaghettidetective.com/docs/user_guides/relink-octoprint/) to get it back in TSD.

If you didn't receive email from us, you were not affected.

#### Were self-hosted TSD server affected by the glitch?

Your private server will if **all** of these are true:

1. your private server is exposed to the Internet.
1. You have a reverse proxy, such as nginx sitting in front of the private server.
1. The reverse proxy is configured to not pass the client IP
1. Someone who knows about the address of your server address connects to your server to link his printer while you are trying to link yours.

Please [upgrade the server code](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective#upgrade-server) to get it permanently fixed.

## Detailed timeline

1. 2021-08-19 6:29 AM UTC. The load-balancer was reconfigured. The start of this security vulnerability.
1. 2021-08-19 ~11 AM UTC. One of our engineers (Shutout to Bence Tamas) noticed that he could see other user's printers. He immediately started investigating the problem.
1. 2021-08-19 ~12 PM UTC. The possible cause of the problem (misconfigured load-balancer) was identified. Based on the severity of the problem, we decided to disabled auto-discovery function.
1. 2021-08-19 12:33 PM UTC. A patched version of the server is pushed to production to stop this problem from impacting more users. Also the work started to identified the users who were potentially impacted.
1. 2021-08-19 ~1:30 PM UTC. The first batch of potentially impacted users and printers are identified and disabled.
1. 2021-08-19 ~2 PM UTC. The 2nd batch of potentially impacted users and printers are identified and disabled.
1. 2021-08-19 8:22 PM UTC. We sent an email to all impacted for what happened, with instructions on what they could do to get their printers back.
1. 2021-08-19 9:16 PM UTC. Committed [the code that will prevent the same problem from happening again](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/commit/05898763584743df3a37d1d99eb43c182d3e695f).


## What we have learned

I don't want to sugar-coat this. This is a serious security vulnerability. I created The Spaghetti Detective to let all 3D printing hobbyists have a way to safely monitor their printers from everywhere. **This is the one of the worst mistakes I can make.**

I sincerely apologized to all of you who have bestowed your trust in us when you chose TSD. I have taken pride in what I have done in TSD, but this incident has made it clear that I still need to get better at what I do!

We will immediately start a security audit for our code to plug holes like this. The Spaghetti Detective is open-sourced [here](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective). If you have experience in security, please help us audit the code and [send any vulnerabilities our way](mailto:support@thespaghettidetective.com) if you find them. Transparency and openness are what we believe in.

Last but not least: people are basically good. Plenty of people who commented in [reddit](https://www.reddit.com/r/3Dprinting/comments/p7jdhi/wake_up_this_morning_and_see_this_on_my_3d/) and [TSD's discord server](https://discord.gg/hsMwGpD) voiced their willingness to give us the benefit of doubt. We don't see trolls. We only see awesome 3D printing enthusiasts who are forgiving and willing to help us improve. This has been, and will always be, the ultimate motivation for us to make TSD better, faster, and yes, more secure!

*Kenneth Jiang, Founder of TSD*