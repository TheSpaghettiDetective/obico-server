---
id: how-to-test-failure-detection
title: How can I test if the failure detection actually works?
sidebar_label: See failure detection in action
---

We know The Spaghetti Detective sounds like a magic. So we don't blame you if you want to see it to believe it!

## Upload your previously recorded time-lapse videos {#upload-your-previously-recorded-time-lapse-videos}

If you've been using Octoprint for a while, chances are you might already have a folder of time 3D printing time-lapses laying around.

If you do, you can upload them on the time-lapse page before ever starting a print with The Detective to see for yourself that The Detective really can catch 3D print failures!

While she does sometimes make mistakes, she has successfully caught thousands of print failures all over the globe to date!

:::tip
Upload your time-lapse videos [here](https://app.obico.io/prints/upload/).
:::

## FAQs {#faqs}

### I tried to test if The Detective is any good. I threw a ball of spaghetti on the print bed. But nothing happened. Was The Detective asleep? {#i-tried-to-test-if-the-detective-is-any-good-i-threw-a-ball-of-spaghetti-on-the-print-bed-but-nothing-happened-was-the-detective-asleep}

Kudos to you for trying to spy on The Detective before putting the faith in her to save you from spaghetti monsters. A few reasons why The Detective is not responding to your delicious spaghetti ball:

- When your printer is not printing, The Detective is off duty to catch some sleeps. So you need to start a print in OctoPrint to call her to duty.
- The Detective tries to be adaptive in order to reduce the amount of false alarms. What it means is that during the first several minutes of a print, The Detective will only observe, rather than alarm. Therefore, when she sees a ball of spaghetti at the very first minutes of the print, she will think "No way! I must be wrong here. I will ignore this huge spaghetti ball for this print."

### Gotcha! But then how do I test if The Detective actually does what she claims to? {#gotcha-but-then-how-do-i-test-if-the-detective-actually-does-what-she-claims-to}

Again the easiest way to test if The Detective is worth her while is to upload a time-lapse. However, if you want to see The Detective in action in real time:

1. Start a test print and let it run for at least 5 minutes.
2. Then you can throw in a ball of spaghetti and watch on "My Printers" page to see if it's correctly identified.
3. Leave that spaghetti ball on the bed for a couple minutes to convince The Detective that this spaghetti monster is here to stay, and she should send you an alert via email or text (if you have set the phone number in [Preferences](https://app.obico.io/user_preferences/notification_twilio/)).
