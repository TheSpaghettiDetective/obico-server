"""A notification channel must never make the server send requests to internal addresses,
whichever way its settings are saved."""
import json
import socket
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from app.models import NotificationSetting, User
from .tests import setup_syndicate


# What the made-up host names in these tests resolve to.
DNS = {
    'hooks.example': '93.184.216.34',
    'internal.example': '10.1.2.3',
    'localhost': '127.0.0.1',
}


REAL_GETADDRINFO = socket.getaddrinfo


def fake_getaddrinfo(host, port=None, *args, **kwargs):
    if host in ('redis', 'db'):  # the test's own services, where they run under those names
        return REAL_GETADDRINFO(host, port, *args, **kwargs)
    try:
        socket.inet_pton(socket.AF_INET, host)
        addr = host
    except OSError:
        if host not in DNS:
            raise socket.gaierror(socket.EAI_NONAME, 'Name or service not known')
        addr = DNS[host]
    # The port asked for: the test's Redis can be at localhost, and has to be reachable there.
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (addr, int(port or 0)))]


def fake_gethostbyname(host):
    return fake_getaddrinfo(host)[0][4][0]


@override_settings(SITE_ID=1)
@patch('socket.gethostbyname', side_effect=fake_gethostbyname)
@patch('socket.getaddrinfo', side_effect=fake_getaddrinfo)
class NotificationAddressTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='ssrf@example.invalid', syndicate=setup_syndicate())
        self.client = Client()
        self.client.force_login(self.user)

    def create(self, name, config):
        return self.client.post('/api/v1/notification_settings/', json.dumps({'name': name, 'config': config}),
                                content_type='application/json')

    def patch_setting(self, setting_id, body):
        return self.client.patch(f'/api/v1/notification_settings/{setting_id}/', json.dumps(body),
                                 content_type='application/json')

    def send_test(self, setting_id):
        return self.client.post(f'/api/v1/notification_settings/{setting_id}/send_test_message/')

    # Changing a channel's type runs the new type's check on the stored settings.

    def test_a_channel_cannot_become_a_webhook_to_an_internal_address(self, *_):
        twilio = self.create('twilio', {'phone_country_code': '', 'phone_number': '',
                                        'custom_webhook_URL': 'http://127.0.0.1:9/hook'}).json()
        response = self.patch_setting(twilio['id'], {'name': 'webhook'})
        self.assertEqual(NotificationSetting.objects.get(id=twilio['id']).name, 'twilio')
        self.assertEqual(response.status_code, 400)

    def test_the_email_channel_cannot_become_a_webhook_to_an_internal_address(self, *_):
        email = NotificationSetting.objects.get(user=self.user, name='email')  # every account has one
        self.patch_setting(email.id, {'config': {'custom_webhook_URL': 'http://127.0.0.1:9/hook'}})
        response = self.patch_setting(email.id, {'name': 'webhook'})
        self.assertEqual(NotificationSetting.objects.get(id=email.id).name, 'email')
        self.assertEqual(response.status_code, 400)

    def test_a_channel_cannot_become_discord_with_any_address(self, *_):
        twilio = self.create('twilio', {'phone_country_code': '', 'phone_number': '',
                                        'webhook_url': 'http://127.0.0.1:9/hook'}).json()
        response = self.patch_setting(twilio['id'], {'name': 'discord'})
        self.assertEqual(NotificationSetting.objects.get(id=twilio['id']).name, 'twilio')
        self.assertEqual(response.status_code, 400)

    def test_each_type_keeps_only_its_own_settings(self, *_):
        email = NotificationSetting.objects.get(user=self.user, name='email')
        twilio = self.create('twilio', {'phone_country_code': '', 'phone_number': '', 'custom_webhook_URL': 'x'})
        self.assertEqual(twilio.status_code, 201)
        self.assertEqual(self.patch_setting(email.id, {'config': {'custom_webhook_URL': 'x', 'webhook_url': 'y'}}).status_code, 200)
        for name, setting_id in (('twilio', twilio.json()['id']), ('email', email.id)):
            stored = NotificationSetting.objects.get(id=setting_id).config
            self.assertNotIn('custom_webhook_URL', stored, name)
            self.assertNotIn('webhook_url', stored, name)

    # The webhook check refuses every address that is not on the public internet.

    def test_webhook_refuses_internal_addresses(self, *_):
        for url in ('http://127.0.0.1:9/hook', 'http://169.254.169.254/', 'http://10.0.0.1/',
                    'http://100.64.0.1/', 'http://internal.example/', 'http://[::1]/', 'http://0.0.0.0/'):
            self.assertEqual(self.create('webhook', {'custom_webhook_URL': url}).status_code, 400, url)
        self.assertFalse(NotificationSetting.objects.filter(name='webhook').exists())

    def test_webhook_accepts_a_public_address(self, *_):
        self.assertEqual(self.create('webhook', {'custom_webhook_URL': 'https://hooks.example/x'}).status_code, 201)

    @patch('notifications.plugins.webhook.requests.post')
    def test_webhook_does_not_follow_redirects(self, post, *_):
        post.return_value.is_redirect = False
        setting = self.create('webhook', {'custom_webhook_URL': 'https://hooks.example/x'}).json()
        self.send_test(setting['id'])
        self.assertEqual(post.call_count, 1)
        self.assertIs(post.call_args.kwargs.get('allow_redirects'), False)

    @patch('notifications.plugins.webhook.requests.post')
    def test_webhook_checks_the_address_again_when_sending(self, post, *_):
        # Saved before the check existed, or the name now resolves somewhere else.
        setting = NotificationSetting.objects.create(user=self.user, name='webhook',
                                                     config_json=json.dumps({'custom_webhook_URL': 'http://internal.example/'}))
        response = self.send_test(setting.id)
        post.assert_not_called()
        self.assertNotEqual(response.json().get('status'), 'sent')

    # Apprise addresses get the same internal-address check.

    def test_apprise_refuses_internal_addresses(self, *_):
        for url in ('json://127.0.0.1:9/hook', 'json://10.1.2.3/', 'json://internal.example/',
                    'ntfy://100.64.0.1/topic', 'xml://localhost/'):
            self.assertEqual(self.create('apprise', {'apprise_url': url}).status_code, 400, url)
        self.assertFalse(NotificationSetting.objects.filter(name='apprise').exists())

    def test_apprise_accepts_public_and_service_addresses(self, *_):
        for url in ('json://hooks.example/x', 'tgram://123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsawX/12345'):
            response = self.create('apprise', {'apprise_url': url})
            self.assertEqual(response.status_code, 201, (url, response.content))
            NotificationSetting.objects.filter(name='apprise').delete()

    @patch('apprise.Apprise.notify')
    def test_apprise_checks_the_address_again_when_sending(self, notify, *_):
        setting = NotificationSetting.objects.create(user=self.user, name='apprise',
                                                     config_json=json.dumps({'apprise_url': 'json://internal.example/'}))
        response = self.send_test(setting.id)
        notify.assert_not_called()
        self.assertNotEqual(response.json().get('status'), 'sent')

    # Requests that used to crash the endpoint with HTTP 500.

    def test_a_patch_without_a_type_does_not_crash(self, *_):
        setting = self.create('webhook', {'custom_webhook_URL': 'https://hooks.example/x'}).json()
        self.assertEqual(self.patch_setting(setting['id'], {'enabled': False}).status_code, 200)
        self.assertEqual(self.patch_setting(setting['id'], {'config': {'custom_webhook_URL': 'http://10.0.0.1/'}}).status_code, 400)
        self.assertEqual(NotificationSetting.objects.get(id=setting['id']).config['custom_webhook_URL'], 'https://hooks.example/x')

    def test_an_unknown_type_is_refused(self, *_):
        self.assertEqual(self.create('no-such-plugin', {}).status_code, 400)

    def test_an_address_that_is_not_text_is_refused(self, *_):
        for name, key in (('webhook', 'custom_webhook_URL'), ('apprise', 'apprise_url'), ('discord', 'webhook_url')):
            self.assertEqual(self.create(name, {key: ['http://10.0.0.1/']}).status_code, 400, name)
