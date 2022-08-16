---
id: print-job-notification-email
title: What's in the email you receive when a print job is done
---

Unless you turned the notifications off, you will receive an email when a print job is done that looks like this:

![](/img/user-guides/print-notification-email-sample.png)

Let's take a look at what each of these paragraphs mean.

## 1. Failure detection {#1-failure-detection}

If The Detective found something during this print, you will see:

<p className="text--danger">The Detective found possible spaghetti for this print.</p>

Otherwise, you will see:

<p className="text--success">The Detective found nothing fishy for this print.</p>

## 2. Feedback {#2-feedback}

Should be quite self-explanatory. This is where you've a chance to [give The Detective feedback to help her get better](/docs/user-guides/how-does-credits-work/).

:::note
Please note [some times there won't be the Focused Feedback link in the email](/docs/user-guides/how-does-credits-work/#why-is-the-focused-feedback-button-missing-from-some-of-my-prints).
:::

## 3. Print job info and AI Detection Hours {#3-print-job-info-and-ai-detection-hours}

:::info
Learn more about [how AI Detection Hour works](/docs/user-guides/how-does-detective-hour-work).
:::

### 3.1 Print time {#31-print-time}

The duration between the time when the print job started and the time when it ended or was cancelled.

:::note
**This print time is NOT the amount of AI Detection Hours you spent on this print. See 3.2 for more details.**
:::

### 3.2 AI failure detection time {#32-ai-failure-detection-time}

This is the amount of time Obico's AI spent on detecting for failures. This is also the amount deducted from your AI Detection Hours balance.

AI failure detection time can be shorter than the print time because of a few reasons:

* You have [disabled AI failure detection](/docs/user-guides/detective-not-watching/#2-you-have-disabled-the-ai-failure-detection-option) in the app.
* There were periods when your OctoPrint lost Internet connection and sent nothing to The Detective.
* The print was paused during the print. When a print is paused, failure detection is also paused so that you won't waste Detection Hours.
* You have chosen "Don't alert me again" in case of a false alarm.

### 3.3 Your remaining AI Detection Hour balance {#33-your-remaining-ai-detection-hour-balance}

The amount of AI Detection Hours left in your account *after the amount in 3.2 was deducted from the balance*.

:::note
AI Detection Hour balance may be a negative number. [Learn why this is the case](/docs/user-guides/how-does-detective-hour-work/#why-is-my-dh-balance-a-negative-number).
:::

## FAQs {#faqs}

#### Why did I receive this email when I kicked off another print, not when this print was done? {#why-did-i-receive-this-email-when-i-kicked-off-another-print-not-when-this-print-was-done}

This is because when your OctoPrint was not connected to the Internet at the time this print was done. This can happen when:

* The Internet connection happened to be down.
* You turned off the power before OctoPrint had performed all the "routines" to finish up a print.

When this happens, The Spaghetti Detective won't have a chance to send the "done signal" to the server. Hence the server wouldn't know this print is already done until it receives the signal that indicates "a new print has started". At that time, the server will determine the previous print is already done and send out this notification email.

#### Hey the print time is sometimes a lot longer than the actual print time! Why is it the case? {#hey-the-print-time-is-sometimes-a-lot-longer-than-the-actual-print-time-why-is-it-the-case}

For the same reason as the previous question. When the "done signal" is missed and the server doesn't know a print is done until the next print starts, the server won't know the actual time when the previous print was done. So out of the lack of a better option, the server will use the time when the next print starts as the time when the previous print finishes.

Rest assured this will NOT cost you more AI Detection Hours. This is because The Detective will not clock her time when she is not hearing from your OctoPrint. When your OctoPrint is powered off or disconnected to the Internet, The Detective is out of job and hence won't bill you for AI Detection Hours.

#### Why is my DH balance a negative number? {#why-is-my-dh-balance-a-negative-number}

Here is [why](/docs/user-guides/how-does-detective-hour-work/#why-is-my-dh-balance-a-negative-number).