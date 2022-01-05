# Email server setup troubleshooting guide

It isn't uncommon that you can't send emails despite the fact that you have configured your account name and password correctly in `docker-compose.yml`. This is because of increasingly stringent security measurements Gmail and other email providers put in place to fight spam emails. 

Typically for email accounts with 2FA(2 Factor Authentication) you will have to create an App password for devices that do not support 2FA, this will be necessary to do for TSD to correctly send emails. You could disable 2FA but this is not recommended for an account that is important to you, so if you really don't want to create an App password (it's quick) another option is to create an account used solely for email relay and to leave 2FA turned off for said account. 

## Step-by-step email server configuration and trouble-shooting guide

1. Open your docker-compose.yml in your preferred editor of choice.

2. Change the lines to the correct values of your email provider, you can fill in the information with or without quotes except for the EMAIL_PORT, which will NOT work when used with quotes.
NOTE: If using an Outlook account the `DEFAULT_FROM_EMAIL:` needs to be changed to match the email it is being sent from, `EMAIL_HOST_USER:`
For Outlook accounts you can verify your SMTP settings needed under your email account in Settings -> Sync
      ```
      EMAIL_HOST:     # -> such as smtp.gmail.com
      EMAIL_HOST_USER:   # -> such as your email address for a Gmail account
      EMAIL_HOST_PASSWORD:    # -> your email account password, or your app password
      EMAIL_PORT: 587   # Check with your email provider to make sure. DO NOT surround it with quotes. Otherwise email won't be sent!
      EMAIL_USE_TLS: 'True' # -> Still set to True even for Outlook with STARTTLS
      DEFAULT_FROM_EMAIL: 'changeme@example.com'  # -> For Outlook set this to match EMAIL_HOST_USER: field, otherwise it is recommended not to change (Seems to work for Gmail without issue)
      ```
3. For Gmail accounts there are 2 options for successfully sending email, if you are not using 2FA then you will need to make sure that you enable Less secure app access from Gmail -> Manage My Account -> Security.

4. Alternatively with 2FA enabled, can also create an App password in Gmail -> Manage My Account -> Security -> Signing Into Google -> App Passwords and then use this as your value for `EMAIL_HOST_PASSWORD`.

5. For Outlook accounts the options are basically the same, if you are not using 2FA for Outlook then you can just use your credentials you login normally with

6. In Outlook with 2FA enabled, you can create an App password under My Microsoft Account -> Security -> Security Dashboard -> Advanced Security Options -> App Passwords.

7. Once you have your settings correct it is now time to put them to the test!
 
## Test if your email server configuration works

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

2. Click the "Users" link.

3. Select the user to whom you want to send test email.

4. In the "Action" drop down list, select "Send test email". Click "Go".

![Send test email](img/send_test_email.png)

## Troubleshooting with the test email
!!Please note to correctly re-build your Docker container when making changes during troubleshooting to the `docker-compose.yml` file otherwise your changes may not take effect!! (Deleting the container in Docker and then using docker-compose up -d seems to be fastest on W10)

1. If you get a Server Error (500) it is likely that something is wrong with the configuration such as incorrect credentials, port, etc. Check the logs on your web container to see what may have been rejected.

2. If you get a message that your email has been successfully sent but no email arrives, make sure that you have verified the account email in the TSD App under Preferences -> Profile.

3. If it is still not working then please read through everything one more time, and if you still can't figure it out it's probably time to stop by the Discord channel for some help. Ask yourself these questions to help explain the issue, has this account been used successfully before by another service to send e-mail through? Was it previously working with TSD and now it is not? What hardware are you hosting TSD on?
