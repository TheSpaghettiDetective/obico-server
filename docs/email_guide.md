# Email server setup trouble-shooting guide

It isn't uncommon that you can't send emails despite the fact that you have configured your account name and password correctly in `docker-compose.yml`. This is because of increasingly stringent security measurements Gmail and other email providers put in place to fend spam emails.

## Test if your email server configuration works

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

1. Click the "Users" link.

1. Select the user to whom you want to send test email.

1. In the "Action" drop down list, select "Send test email". Click "Go".

![Send test email](img/send_test_email.png)

## Step-by-step email server configuration and trouble-shooting guide

1. Open your docker-compose.yml in your preferred editor of choice
2. Change the lines to the correct values of your e-mail provider, you can fill in the information with or without quotes except for the EMAIL_PORT, which will NOT work when used with quotes
      ```
      EMAIL_HOST:     # -> such as smtp.gmail.com
      EMAIL_HOST_USER:   # -> such as your email address for a Gmail account
      EMAIL_HOST_PASSWORD:    # -> your email account password
      EMAIL_PORT: 587   # Check with your email provider to make sure. DO NOT surround it with quotes. Otherwise email won't be sent!
      EMAIL_USE_TLS: 'True'
      ```
3. For GMail accounts there are 2 options for successfully sending e-mail, you will have to allow Less Secure Apps and in order to do so you must disable 2FA Authentication. You can also create an App password in Gmail under the Security section and use this as your value for EMAIL_HOST_PASSWORD.
4. For Outlook accounts you can verify your settings needed under your E-mail account in Settings>Sync
5. Once you have your settings correct you can navigate to the Django admin page at `http://your_server_ip:3334/admin/`. and send a test e-mail
6. If you get a Server Error 500 there is something wrong with the configuration such as incorrect password, port etc
7. If you get a message that your e-mail has been successfully sent but no e-mail arrives, make sure that you have verified the account e-mail in the App
8. If it is still not working then it's probably time to stop by the Discord channel for some help
