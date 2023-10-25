import time
from locust import HttpUser, TaskSet, events, task, between, run_single_user
from locust.env import Environment
from requests.auth import HTTPBasicAuth

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

IMAGE_CONTENT = None
AUTH_TOKEN = None
TEST_ADMIN_CREDENTIALS = ('test@test.com', 'test')
TEST_PRINTER_ID = 1


@events.test_start.add_listener
def get_image_content(environment: Environment, **kwargs):
    with open('/backend/static_build/media/tsd-pics/snapshots/1/latest_unrotated.jpg', 'rb') as file:
        global IMAGE_CONTENT
        IMAGE_CONTENT = file.read()


@events.test_start.add_listener
def admin_login(environment: Environment, **kwargs):
    """Log in as admin user so we can query the web view APIs"""
    print("Logging in admin")
    HttpUser.host = environment.host
    admin_user = HttpUser(environment=environment)
    response = admin_user.client.get("/accounts/login/")
    csrf_token = response.cookies.get('csrftoken', None)
    if csrf_token is None:
        raise ValueError("Could not get a valid csrftoken")
    admin_user.client.post(
        url="/accounts/login/",
        data={
            'login': TEST_ADMIN_CREDENTIALS[0],
            'password': TEST_ADMIN_CREDENTIALS[1],
            'csrfmiddlewaretoken': csrf_token
        },
    ).raise_for_status()
    response = admin_user.client.get(f"/api/v1/printers/{TEST_PRINTER_ID}/")
    response.raise_for_status()
    global AUTH_TOKEN
    AUTH_TOKEN = response.json()['auth_token']
    print(f"Finished setting auth token: {AUTH_TOKEN}")


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
            print(f"AUTH_TOKEN: {AUTH_TOKEN}")
            print(f"IMAGE_CONTENT: {IMAGE_CONTENT}")
            raise ValueError("Must set a valid auth_token and image_content before proceeding")

    @task
    def octo_pic(self):
        self.client.post(
            url='/api/v1/octo/pic/',
            files={'pic': self.image_content},
            headers={'Authorization': f'Token {self.auth_token}'},
            cookies=None
        ).raise_for_status()


if __name__ == "__main__":
    run_single_user(PrinterUser)
