import time

from django.test import Client, TestCase, override_settings

from app.models import Printer, SharedResource, User
from api.serializers import PublicPrinterSerializer
from lib import relay
from .tests import setup_syndicate

STUN = ['stun:stun.l.google.com:19302']
VIEWER_URLS = ['turns:relay.example.invalid:443?transport=tcp', 'turn:relay.example.invalid:80?transport=udp']
PRINTER_URLS = ['turn:relay.example.invalid:80?transport=tcp']
RELAY_ON = dict(RELAY_HOST='relay.example.invalid', RELAY_SECRETS=['test-secret-one', 'test-secret-old'])
RELAY_OFF = dict(RELAY_HOST=None, RELAY_SECRETS=[])


class RelayCredentialTestCase(TestCase):

    def test_the_password_is_coturns_hmac_of_the_username(self):
        # The expected value comes from: printf %s "1700000000:p42" | openssl dgst -sha1 -hmac "test-secret-one" -binary | base64
        self.assertEqual(relay.credential_password('1700000000:p42', 'test-secret-one'), 'n68hkUDRfqdaVkwYsZ1Ah5k3VLE=')


@override_settings(SITE_ID=1)
class RelayInPrinterResponsesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='relay@example.invalid', syndicate=setup_syndicate(), is_pro=True)
        self.printer = Printer.objects.create(user=self.user, name='p', auth_token='relay-test-token')
        self.web = Client()
        self.web.force_login(self.user)

    def plugin_relay(self):
        resp = Client().get('/api/v1/octo/printer/', HTTP_AUTHORIZATION=f'Token {self.printer.auth_token}')
        self.assertEqual(resp.status_code, 200)
        return resp.json()['printer']['relay']

    def owner_relay(self):
        resp = self.web.get(f'/api/v1/printers/{self.printer.id}/')
        self.assertEqual(resp.status_code, 200)
        return resp.json()['relay']

    def shared_relay(self):
        SharedResource.objects.create(printer=self.printer, share_token='relay-share-token')
        return PublicPrinterSerializer(self.printer).data['relay']

    def assert_relay(self, got, urls, name, lifetime_secs):
        self.assertEqual(got['ice_servers'][0], {'urls': STUN})
        server = got['ice_servers'][1]
        self.assertEqual(server['urls'], urls)
        expires_at, got_name = server['username'].split(':')
        self.assertEqual(got_name, name)
        self.assertEqual(int(expires_at), got['expires_at'])
        self.assertAlmostEqual(got['expires_at'], time.time() + lifetime_secs, delta=60)
        # Signed with the first secret, which is what the relay checks first.
        self.assertEqual(server['credential'], relay.credential_password(server['username'], 'test-secret-one'))

    @override_settings(**RELAY_ON)
    def test_the_printer_gets_its_own_tcp_relay_for_a_week(self):
        self.assert_relay(self.plugin_relay(), PRINTER_URLS, f'p{self.printer.id}', 7 * 24 * 3600)

    @override_settings(**RELAY_ON)
    def test_the_owners_page_and_app_get_the_viewer_relay_for_a_day(self):
        self.assert_relay(self.owner_relay(), VIEWER_URLS, f'v{self.printer.id}', 24 * 3600)

    @override_settings(**RELAY_ON)
    def test_a_shared_link_viewer_gets_a_name_of_its_own(self):
        self.assert_relay(self.shared_relay(), VIEWER_URLS, f's{self.printer.id}', 24 * 3600)

    @override_settings(**RELAY_ON)
    def test_no_response_carries_the_printer_token_as_a_relay_credential(self):
        for got in (self.plugin_relay(), self.owner_relay(), self.shared_relay()):
            self.assertNotIn(self.printer.auth_token, str(got))

    @override_settings(**RELAY_OFF)
    def test_without_relay_settings_clients_get_stun_only(self):
        for got in (self.plugin_relay(), self.owner_relay(), self.shared_relay()):
            self.assertEqual(got, {'ice_servers': [{'urls': STUN}], 'expires_at': None})
