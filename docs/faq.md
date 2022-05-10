# Frequently Asked Question

## I can't see webcam feed on the TSD page of my own server. How can I figure out what went wrong.

There are several ways to further debug this issue.

### Rule out the basics.

Follow [these steps](https://www.obico.io/docs/user-guides/webcam-feed-is-not-showing/) to make sure your TSD plugin, as well as the webcam, is configured correctly.

### If the Server Connection Test returns successfully, but you still can't see the webcam.

In this case, you can download the "octoprint.log" ([here is how](https://community.octoprint.org/t/where-can-i-find-octoprints-and-octopis-log-files/299))file and check for any errors.

For instance, if you are seeing the errors similar to:

    2019-04-15 15:09:28,108 - backoff - INFO - Backing off capture_jpeg(...) for 14.4s (ConnectionError: HTTPConnectionPool(host='192.168.134.40', port=8081): Max retries exceeded with url: /?action=snapshot (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fdc4d712e50>: Failed to establish a new connection: [Errno 111] Connection refused',)))

it means TSD plugin can't access the configured webcam URL.

### You are seeing error message after pressing the "Test" button on TSD settings page.

Most likely you will see <span style="color:red">Failed to contact server. Is OctoPrint connected to Internet?</span>.

![server connection error](img/onpremise-server-error.png)

 This error is quite general and vague (because it needs to be understadable for users who are not tech-savvy). You can do a few things to dig further:

- SSH to the computer on which OctoPrint runs, most likely a Raspberry Pi, and test the connectivity to your server by running `curl http://your_serer_ip:3334/`. If the connection to the server is successful, you won't see any error message. If, instead, you see error messages such as `curl: (7) Failed to connect to 10.0.2.2 port 333: Connection refused`, you need to fix the connectivity issue (could be routing, firewall, etc) from your OctoPrint to your server.

- Check server logs by running `cd TheSpaghettiDetective && sudo docker-compose logs web`. Look for errors in the output.

### If you still can't get webcam feed after going through all these steps above, please [submit a github issue](https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/new) and provide as much details as you can in the issue.
