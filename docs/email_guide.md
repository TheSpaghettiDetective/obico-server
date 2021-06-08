# Email server setup trouble-shooting guide

It isn't uncommon that you can't send emails despite the fact that you have configured your account name and password correctly in `docker-compose.yml`. This is because of increasingly stringent security measurements Gmail and other email providers put in place to fend spam emails.

## Test if your email server configuration works

1. Open Django admin page at `http://your_server_ip:3334/admin/`.

1. Click the "Users" link.

1. Select the user to whom you want to send test email.

1. In the "Action" drop down list, select "Send test email". Click "Go".

![Send test email](img/send_test_email.png)

## Step-by-step email server configuration and trouble-shooting guide

*Help needed to finish this section!*
