import json
import time
import random

from locust import HttpUser, events, task, run_single_user, tag, between
import greenlet
from locust.env import Environment
from locustfile import WebUserBase

# START DEBUG SETTINGS

# import logging
# from http.client import HTTPConnection
#
# HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# END DEBUG SETTINGS

# Test account credentials and target printer_id

WEB_URL = 'http://web:3334'
INTERNAL_IMG_URL = None


@events.test_start.add_listener
def set_internal_img_url(environment: Environment, **kwargs):
    print("Logging in admin to web")
    WebUserBase.host = WEB_URL
    admin_user = WebUserBase(environment=environment)
    admin_user.host = WEB_URL
    admin_user.client.host = WEB_URL
    admin_user.login()
    global INTERNAL_IMG_URL
    INTERNAL_IMG_URL = admin_user.get_internal_image_url()
    print(f"Set INTERNAL_IMG_URL to {INTERNAL_IMG_URL}")

@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    print("Test started!")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test has ended!")

class MlApiUser(HttpUser):
    internal_img_url = ''

    def on_start(self):
        # Get internal image URL for api testing
        self.internal_img_url = WebUserBase(environment=self.environment)
        self.internal_img_url = INTERNAL_IMG_URL
        if self.internal_img_url is None:
            greenlet.error("internal_img_url is None")

    @task
    def prediction(self):
        self.client.get('/p/', params={'img': self.internal_img_url})


if __name__ == "__main__":
    run_single_user(MlApiUser)
