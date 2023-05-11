---
title: Configure a Gmail account as SMTP server to send emails
---

To use Gmail's SMTP server for sending email, follow the following simple steps.

## 1. Make sure the 2-Step Verification is turned on for the Gmail account. {#1-make-sure-the-2-step-verification-is-turned-on-for-the-gmail-account}

Follow [this guide](https://support.google.com/accounts/answer/185839) to turn on 2-Step Verification.

## 2. Add an "app password" for your self-hosted Obico server. {#2-add-an-app-password-for-your-self-hosted-obico-server}


1. Go to the [Google app passwords](https://myaccount.google.com/apppasswords)
2. sign in to the Gmail account you intend to use.
3. At the bottom, choose "Select app", and "Other (Custom name)".
4. Choose a name for this app password, such as "My Obico server".
5.  Click "Generate".
6. On the next screen, copy the text in the yellow box. This is the pass you will use in the next step.



![Site configuration](/img/server-guides//gmail_setup_2.png)

![Site configuration](/img/server-guides//gmail_setup_3.png)

![Site configuration](/img/server-guides//gmail_setup_4.png)

If you run into issues creating an app password, you can check out [Google's guide](https://support.google.com/mail/answer/185833?hl=en).

## 3. Configure `.env` with the correct email settings. {#3-configure-env-with-the-correct-email-settings}

```
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=the_full_email@gmail.com
EMAIL_HOST_PASSWORD=the_app_password_you_copied_from_previous_step
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

:::tip
If you can't find the `.env` file, check out [this guide](../configure.md/#email-smtp).
:::

## 4. Restart the server. {#4-restart-the-server}

`docker compose up --build -d`

## 5. Send a test email {#5-send-a-test-email}

Follow [this guide](email_guide.md/#test-if-your-email-server-configuration-works) to send a test email.
