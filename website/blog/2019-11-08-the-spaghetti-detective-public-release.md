---
title: The Spaghetti Detective Public Launch Annoucement
author: Kenneth Jiang
author_url: https://medium.com/@kennethjiang
author_image_url: https://www.thespaghettidetective.com/img/kj.jpg
tags: ['The Spaghetti Detective Updates']
---

The Spaghetti Detective has come out of beta! With improved AI accuracy, and shiny new user experience such as the [sleek 25-frames-per-second webcam streaming](/blog/2019/09/17/video-streaming-in-octoprint), we are open to all 3D printing enthusiasts now!

<!--truncate-->

## What's included in the new version?

Real video streaming (based on H.264 encoding) is by far the coolest feature in our public release. After thoroughly testing it for a full month and bug-fixing, this video streaming now works for almost all kinds of webcams, including Pi Camera and the popular Logitech webcams.

Of course, we have also improved the accuracy of the AI model based on [the feedback all beta testers have given to The Detective](/docs/how-does-detective-hour-work).

## Now does it cost me to let The Detective watch my prints?

Yes and No.

We TSD team feel really proud of what we have built, and we want to make TSD as accessible as possible to 3D printing enthusiasts like you and me. So we will always have  **the Free plan** for people who are on a budget. If you have only 1 printer, and you don't print a lot, the Free plan is possibly good enough for you. The Free plan includes 10 free Detective Hours **each month**. It doesn't sound like a lot. But if you turn on "Detective Watching" mode only for your risky prints, it may be good enough and it may save you the day, or a damaged equipment in some cases.

If you do have multiple printers and/or print a lot, and subscription is not your cup of tea (or should we say your plate of spaghetti?), you can set up your own TSD server based on our [open source project](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective).

Of course, if you don't appreciate the hassle of running your own server, DNS, firewall, etc, and you print too much for the Free plan, Pro plan starts only as little as $5.5/month. If you subscribe to the annual plan it's only **$4/month**, barely a Starbucks coffee. The Pro plan also allows you to more Detective Hours with [a Subscribe&Save Pack](https://app.thespaghettidetective.com/ent_pub/pricing/#need-more) at rates much lower than the ones available to the Free plan users.

## Well, why don't you just make TSD free for everyone!

We wish we could do that too! The people at TSD team are all nerds and we all love 3D printing, so it's super rewarding for us to use cool technology as AI to give our fellow 3D printing folks a peace of mind.

However, hosting TSD server in the cloud is not cheap, and we can't cover that cost out of our pocket forever. Especially the AI failure detection relies on GPUs, a special computer hardware that are super expensive to run in the cloud. Also our users are sending **tens of terabytes** per month to our servers, which means pretty steep bills from our cloud provider each month.

We have optimized our infrastructure a lot to get the cost as low as possible, but it's still very substantial given the number of users we have. We have to figure out a way to make TSD self-sustainable because we don't want see this cool project loved by a lot of people to be dead in the water!

We have also tried very hard to figure out a pricing that is as fair, as affordable as it can be. For instance, after talking to tens of beta testers, we found out that some users just need webcam streaming and don't want to pay extra for automated failure detection. That's why we devised the ["Detective Hour Packs"](https://app.thespaghettidetective.com/ent_pub/pricing/#need-more) so that those expensive GPUs are only used for the users who really want it.

## What will happen to my beta account?

On November 10th, unlimited usage for all beta accounts will end. You can still login with your beta account, but if you want to continue to enjoy the full set of features, and have prints watched by The Detective at all times, please check out our new pricing page and upgrade to the appropriate plan.

You can also choose to not to upgrade. In this case, your account will be converted to the Free plan. Remember that you will still get 10 free Detective Hours each month on the Free plan.

## What if I have more than 1 printers in my beta account and I decide to stay with the Free plan?

We will archive your printers except the one that you added most recently. You will see a warning message at the top of TSD's printer page with a link to see all these archived printers.

![Archived printers](/img/blogs/archived_printers.png)

If your most-recently-added printer is not the one you want to keep in TSD, you can delete it and make room for that printer you want. Once you delete your active printer, you can click the link in the message to a list of archived printers. From there, you can un-archive the printer you want to have in TSD.

## What happened to all the DG credits I have previously earned?

First of all, thank you for contributing to our project by helping The Detective get better.

We have converted all DGs to Detective Hours at 1:1 ratio.

You can check all of them [here](https://app.thespaghettidetective.com/ent/detective_hours/).

## What if I already have an OctoPrint Anywhere subscription?

To thank you for being an early support of OctoPrint Anywhere, we will give you the Pro plan for free. If you are using the same email address in both OctoPrint Anywhere and TSD, nothing needs to be done. Your TSD account is already set up with the Pro plan up to the number of printers you have in OctoPrint Anywhere.

If you use different email address for your OctoPrint Anywhere subscription, please [email us](mailto:support@thespaghettidetective.com) and we will get it sorted out.
