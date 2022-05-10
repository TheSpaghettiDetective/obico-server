---
title: The Spaghetti Detective Is Now Obico
author: Obico Team
author_url: https://obico.io/team.html
author_image_url: https://www.obico.io/img/favicon.png
---

![Screen](/img/blogs/the-spaghetti-detective-is-now-obico.gif)

Since releasing The Spaghetti Detective in 2019, it has grown to become the most popular software for 3D printing failure detection. If you have been using The Spaghetti Detective for some time, you already know we do much more than failure detection.

## Why did you change the name? I liked The Spaghetti Detective

Over the past couple of years, failure detection has remained at our core, but we have also added new features driven by user feedback such as a mobile app for monitoring and controlling your 3D printer from anywhere, OctoPrint Tunneling, and more. As we have expanded the software, we felt that our name, “The Spaghetti Detective” wasn’t quite able to describe all of the great features that our users have come to appreciate.

We think Obico will better reflect our mission to build software that makes 3D printers smarter and empowers makers like you to use 3D printers to their fullest potential.

Say hello to [Obico  the open-source, community-built, smart 3D printing platform](https://obico.io)!

![](/img/blogs/obico-logo-square-dark-1080.jpeg)

## Okay, but how is this different from The Spaghetti Detective? Did you just change the name?

Obico has similar characteristics to The Spaghetti Detective, but there are also some differences. We will explain some of the differences below.

### Smart 3D Printing?

Call it what you want, but we are talking about connected devices. Speakers, watches, and even toasters are smart devices these days. We think 3D printers should work for you not against you, and making them smarter is a great way to start! In that regard, not much has changed. Part of our mission has always been to make 3D printers easier and more accessible for makers and hobbyists, and we will continue with that mission.

### Multi-Platform

Our goal is to make the best 3D printing software available to as many makers as possible. In the past, we focused on making The Spaghetti Detective compatible with OctoPrint, but many users told us that they were now using Klipper.


A few months ago, we released the alpha version of our moonraker integration, and despite how raw it was, many users let us know that we were headed in the right direction. So, we are excited to announce that with the launch of Obico, also comes the launch of our [Obico for Klipper Beta](https://obico.io/docs/user-guides/klipper-setup). You can now remotely monitor and control your Klipper-connected 3D printer from anywhere and get 3D printing peace of mind with AI failure detection.




### Open-Source

Some of you may not already know that much of The Spaghetti Detective was already open-source since day one. Obico will remain 100% open-source, and because we are huge believers that the open-source model and community-built projects are the best way to make 3D printers better, we are putting open-source upfront. We have completely revamped our open-source documentation and added new features such as a public API, a customizable user interface, and more.

Many of you have asked us if/when we will open-source the mobile app. We are working on it! Open-sourcing a mobile app is trickier than a web app because mobile apps don’t have an easy way to separate API keys and other credentials from the code the way that web apps do. But we are pretty close. Add [support@obico.io](mailto:support@obici.io) to your contact list When the open-source mobile app is ready, we will announce it in our monthly newsletter.

Many hardworking, 3D printing lovers in our community have already contributed to the project in the past. We are hoping more of you will contribute as the Obico smart 3D printing platform grows. [Learn more about how to contribute](https://www.obico.io/docs/developer-guides/contribute/).


### Public APIs!

As a community, you have communicated your message loud and clear: you want us to open the public APIs so you can build fun projects by talking directly to the server or automating your print farm workflow. Now [you've got it](https://www.obico.io/docs/api/)!


### A Wealth of Documentations for Self-Hosting

For those of you who have been itching to self-host your own Obico Server, but struggled to do so because of a lack of good documentation, we’ve got good news for you. We have rewritten many of the [documents for self-hosting](https://www.obico.io/docs/server-guides/) and reorganized them so they are easier to follow.



### The Plugins!

Yes! You heard it right. The Obico Server [now supports plugins](https://www.obico.io/docs/developer-guides/plugins/)! This means the maximum flexibility to customize your self-hosted server. It also makes it easier for everyone to contribute to the source code. Win-Win!




## Does the Obico Cloud have a different pricing plan than The Spaghetti Detective?



The Obico Cloud keeps the same Pro pricing as The Spaghetti Detective. The only change we made was to remove the “Shop Plan”. Although the Shop Plan would deliver more revenue per customer for us, it has distracted us from making the app better for hobbyists. Plus, most print farms are perfectly happy with the Pro plan.

## What does the transition mean for current users of The Spaghetti Detective?

We have done the plumbing work to make moving to Obico as smooth as possible for you. All your current settings in your The Spaghetti Detective account have been migrated to Obico.
Based on your current setup, you may need to make the following changes:





### Website and Web App

You can sign into the Obico Cloud web app at [app.obico.io](https://app.obico.io/accounts/login/) or [obico.io](https://www.obico.io). Don’t worry, if you forget and go to [thespaghettidetective.com](https://obico.io) or [app.thespaghettidetective.com](https://app.obico.io) by accident, we will point you in the right direction!



### Mobile App

No changes are needed: The Spaghetti Detective mobile app has been transitioned to the Obico App for both iOS and Android. If you haven’t already, update The Spaghetti Detective app in the Apple App Store or the Google Play Store, and you will have the sleek new Obico mobile app.



### Payment Processing

No changes are needed: We have seamlessly transitioned your account and payment processing information. Payments are processed by Chargebee as they have been in the past.




### OctoPrint Users

If you are using OctoPrint, you will need to uninstall The Spaghetti Detective Plugin (keep data) and install the new [Obico Plugin](https://octoprint.org/plugins/obico). Once you restart OctoPrint, your curent settings in The Spaghetti Detective Plugin will be automatically migrated to the new Obico plugin.

Find more details in [this guide](https://www.obico.io/docs/user-guides/move-from-tsd-to-obico-in-octoprint/) in case you run into problems.



### Klipper Users (not using OctoPrint)

If you are using Klipper with Mainsail and Fluidd, you can follow [this guide](https://obico.io/docs/user_guides/klipper-setup) to get started with Obico for Klipper. Remember, it is a beta release, so [providing feedback and reporting any bugs](https://github.com/TheSpaghettiDetective/moonraker-obico/issues) is greatly appreciated!




## I am running a self-hosted The Spaghetti Detective server. What should I do?

```
cd TheSpaghettiDetective
git remote remove origin
git remote add origin https://github.com/TheSpaghettiDetective/obico-server.git
git fetch
git checkout release
docker-compose up --build -d
```

## We are expanding the core team. We need you!

We have deferred some of your feature requests because Obico is still a tiny team. The good news is our users’ enthusiasm has allowed us to grow at a rapid clip. Now our cash flow is at a point that allows us to hire 1 full-time engineer or 2 part-time ones.

If you are a talented programmer, and you feel that you are wasting your time being a cog in a big wheel, come join us!

**What you will get:**

- An environment in which you can not only decide how you want to do things, but also what should be done. Yes, we mean it. It’s not a stretch for anyone in the team to say “Changing the name to Obico was a dumb idea. Let’s switch back to The Spaghetti Detective!”. There is no taboo in Obico.
- Work with people who are makers. Build a product that are loved by makers. Hear from our users on regular basis: "Oh I love Obico! I can't 3D print with it. Let me support you with my subscription. And tell me how else I can help you succeed!".
- Tons of challenges that are unimaginable even for a much bigger team. How can we process 5TB data a week while providing a sub-150ms server response time? How can we maintain the server available at four 9s? How can we do that at a budget that is a fraction of what most other team will need to pull it off?
- Market-average cash income. Through-the-roof fun!
- Above all, the possibility of leaving a dent on the journey toward Smart 3D Printing!

**What you won't get:**

- Cash compensation that is a lot higher than your local market. If you look for money, don't join Obico! But you will have a good chunk of Obico's equity, and tons of influence on how Obico should be built.
- People telling you what to do. You are expected to be extremely autonomous. We hope you won't mind that. ;)
- Wasting your time on the things that you don't believe in. If you don't believe in meetings. Don't come to the meetings. If you don't believe in documentations, don't do it. You just need to be accountable for the consequence of your action.

[Write to us](mailto:support@obico.io) if you feel this is the right calling. Don't send us your resume. We don't read those things.

## We’re Just Getting Started

Over the past couple of years, we have grown from a community of a couple of thousand 3D printing hobbyists into a much larger one with over 100,000. We are extremely grateful to everyone that has supported the project up until this point, and we are excited to continue to grow Obico into a powerful all in one smart 3D printing platform. As always, we welcome any and all feedback and suggestions from the community, so if you have any feedback or anything else to say, please [let us know](mailto:support@obico.io)!


