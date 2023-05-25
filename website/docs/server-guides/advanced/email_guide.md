---
title: Email setup troubleshooting guide
---

It isn't uncommon that you can't send emails despite the fact that you have configured your account name and password correctly in `.env`. This is because of increasingly stringent security measurements Gmail and other email providers put in place to fight spam emails.

Typically for email accounts with 2FA (2 Factor Authentication) you will have to create an App password for devices that do not support 2FA, this will be necessary to do for Obico to successfully send emails. You could disable 2FA but this is not recommended for an account that is important to you, so if you really don't want to create an App password (it's quick) another option is to create an account used solely for email relay and to leave 2FA turned off for said account.

## Step-by-step email server configuration and trouble-shooting guide {#step-by-step-email-server-configuration-and-trouble-shooting-guide}

1. Open `obico-server/.env` in your preferred editor of choice.

2. Change the lines to the correct values of your email provider.

NOTE: If using an Outlook account the: `DEFAULT_FROM_EMAIL:` needs to be set to match your: `EMAIL_HOST_USER:`

For Outlook there are a few different SMTP settings, you can verify which are needed for your email under your: Account -> Settings -> Sync.


      EMAIL_HOST=smtp.gmail.com    # -> such as smtp.gmail.com
      EMAIL_HOST_USER=changeme@example.com  # -> such as your email address for a Gmail account
      EMAIL_HOST_PASSWORD="fakepassword  # -> your email account password, or your app password
      EMAIL_PORT=587   # Check with your email provider to make sure. DO NOT surround it with quotes. Otherwise email won't be sent!
      EMAIL_USE_TLS=True # -> Still set to True even for Outlook with STARTTLS
      DEFAULT_FROM_EMAIL=changeme@example.com  # -> For Outlook set this to match EMAIL_HOST_USER: field, otherwise it is recommended not to change (Seems to work for Gmail without issue)

### Gmail {#gmail}

You can follow [this guide](gmail_smtp_setup_guide.md) if you want to use a Gmail account to send emails.

### Outlook {#outlook}
Without using 2FA you can just use your normal login credentials.

With 2FA enabled, you can create an App password under: My Microsoft Account -> Security -> Security Dashboard -> Advanced Security Options -> App Passwords.

## Test if your email server configuration works {#test-if-your-email-server-configuration-works}

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

2. Click the "Users" link.

3. Select the user to whom you want to send test email.

4. In the "Action" drop down list, select "Send test email". Click "Go".

![Send test email](/img/server-guides/send_test_email.png)

## Troubleshooting with the test email {#troubleshooting-with-the-test-email}
Ensure you are correctly re-building your Docker container with the command ```docker compose up --build -d``` (use sudo in front for Linux) when making changes during troubleshooting to the `docker-compose.yml` file otherwise your changes may not take effect!

1. If you get a Server Error (500) it is likely that something is wrong with the configuration such as incorrect credentials, port, etc. Check the logs on your web container to see what may have been rejected.

2. If you get a message that your email has been successfully sent but no email arrives, make sure that you have verified the account email in the Obico App under Preferences -> Profile.

3. If it is still not working then please read through everything one more time, and if you still can't figure it out it's probably time to stop by the [Discord](https://obico.io/discord) channel for some help. Ask yourself these questions ahead of time to help explain the issue, has this account been used successfully before by another service to send e-mail through? Was it previously working with Obico and now it is not? What hardware are you hosting Obico Server on? Any other functions of Obico Server not working?
