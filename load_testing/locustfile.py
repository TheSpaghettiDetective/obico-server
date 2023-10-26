import time
import random

from locust import HttpUser, events, task, run_single_user, tag, between
import greenlet
from locust.env import Environment

# START DEBUG SETTINGS

# import logging
# from http.client import HTTPConnection

# HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# END DEBUG SETTINGS

# Test account credentials and target printer_id
TEST_ADMIN_CREDENTIALS = ('test@test.com', 'test')
TEST_PRINTER_ID = 1

# Init global variables
IMAGE_CONTENT = None
AUTH_TOKEN = None

@events.test_start.add_listener
def get_image_content(environment: Environment, **kwargs):
    with open('/backend/static_build/media/tsd-pics/snapshots/1/latest_unrotated.jpg', 'rb') as file:
        global IMAGE_CONTENT
        IMAGE_CONTENT = file.read()


@events.test_start.add_listener
def set_printer_auth_token(environment: Environment, **kwargs):
    """Log in as admin user so we can query the web view APIs"""
    print("Logging in admin")
    WebUser.host = environment.host
    admin_user = WebUser(environment=environment)
    admin_user.login()
    response = admin_user.client.get(f"/api/v1/printers/{TEST_PRINTER_ID}/")
    response.raise_for_status()
    global AUTH_TOKEN
    AUTH_TOKEN = response.json()['auth_token']
    print(f"Finished setting printer auth token: {AUTH_TOKEN}")


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    print("Test started!")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test has ended!")


class PrinterUser(HttpUser):
    auth_token = None
    image_content = None

    def on_start(self):
        global AUTH_TOKEN
        global IMAGE_CONTENT
        self.auth_token = AUTH_TOKEN
        self.image_content = IMAGE_CONTENT
        if None in [self.auth_token, self.image_content]:
            if self.auth_token is None:
                print(f"AUTH_TOKEN: {self.auth_token}")
            if self.image_content is None:
                print(f"IMAGE_CONTENT: {IMAGE_CONTENT}")
            raise greenlet.error("Must set a valid auth_token and image_content before proceeding")

    @tag('octoprint')
    @task(10)
    def octo_pic(self):
        self.client.post(
            url='/api/v1/octo/pic/',
            files={'pic': self.image_content},
            headers={'Authorization': f'Token {self.auth_token}'},
            cookies=None
        ).raise_for_status()

class WebUserBase(HttpUser):
    auth_token = ''
    environment: Environment
    abstract = True

    def on_start(self):
        self.login()


    def login(self):
        retries = 0
        while not self.client.cookies.get_dict().get('tsd_sessionid'):
            response = self.client.get("/accounts/login/")
            csrf_token = response.cookies.get('csrftoken', None)
            if csrf_token is None:
                raise ValueError("Could not get a valid csrftoken")

            if retries:
                print(f"Retrying login {retries}")
            response = self.client.post(
                url="/accounts/login/",
                data={
                    'login': TEST_ADMIN_CREDENTIALS[0],
                    'password': TEST_ADMIN_CREDENTIALS[1],
                    'csrfmiddlewaretoken': csrf_token
                },
                allow_redirects=False
            )
            response.raise_for_status()
            tsd_sessionid = response.cookies.get('tsd_sessionid', None)
            self.client.cookies['tsd_sessionid'] = tsd_sessionid
            retries += 1
            if tsd_sessionid is None:
                time.sleep(random.randint(1, 5))
        if retries > 1:
            print(f"Finally got a session after {retries} retries")

    def get_internal_image_url(self, web_host='http://web:3334', printer_id=TEST_PRINTER_ID):
        response = self.client.get(f'{web_host}/api/v1/printers/{printer_id}/')
        response.raise_for_status()
        resp_json: dict = response.json()
        print(resp_json)
        if 'pic' not in resp_json.keys():
            return None
        if 'img_url' not in resp_json['pic'].keys():
            return None
        return resp_json['pic']['img_url']

class WebUser(WebUserBase):
    abstract = False

    @tag('web')
    @task(1)
    def printers(self):
        response = self.client.get('/api/v1/printers/')
        response.raise_for_status()

    @tag('web')
    @task(2)
    def printer(self):
        response = self.client.get(f'/api/v1/printers/{TEST_PRINTER_ID}/')
        response.raise_for_status()


if __name__ == "__main__":
    run_single_user(PrinterUser)
