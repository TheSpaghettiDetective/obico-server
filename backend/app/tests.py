import os
import tempfile
import uuid
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, RequestFactory, SimpleTestCase, TestCase, TransactionTestCase
from django.utils import timezone
from unittest.mock import ANY, patch, PropertyMock
from packaging.version import InvalidVersion
from requests import Response
from requests.exceptions import HTTPError

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

from app.accounts import SyndicateSpecificAccountAdapter, users_by_email
from app.forms import SyndicateSpecificResetPasswordForm
from app.models import GCodeFile, MobileDevice, NotificationSetting, Print, Printer, PrinterEvent, User, SiteSyndicate
from app.models.syndicate_models import Syndicate
from app.views.tunnelv2_views import is_plugin_version_supported
from lib import mobile_notifications
from lib.url_signing import HmacSignedUrl, new_signed_url
from lib.utils import get_rotated_pic_url
from lib import syndicate as syndicate_lib
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class PrinterEventTestCase(TestCase):

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
        site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'testserver', 'name': 'testserver'})
        SiteSyndicate.objects.update_or_create(site=site, defaults={'syndicate': syndicate})
        self.user = User.objects.create(email='event@test.com', syndicate=syndicate)
        self.printer = Printer.objects.create(user=self.user)
        self.print = Print.objects.create(
            user=self.user,
            printer=self.printer,
            filename='old.gcode',
            ext_id=1,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )

    def test_event_create_uses_existing_image_url(self):
        with patch('app.models.other_models.get_rotated_pic_url') as snapshot, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(
                print=self.print,
                event_type=PrinterEvent.STARTED,
                image_url='provided-image-url',
                task_handler=True,
            )

        snapshot.assert_not_called()
        self.assertTrue(PrinterEvent.objects.filter(image_url='provided-image-url').exists())

    def test_event_create_saves_missing_ok_snapshot_to_short_term_storage(self):
        with patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url') as snapshot, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED, task_handler=True)

        snapshot.assert_called_once_with(
            self.printer,
            force_snapshot=True,
            missing_ok=True,
        )
        self.assertTrue(PrinterEvent.objects.filter(image_url='event-image-url').exists())

    def test_event_text_escapes_printer_name_and_filename(self):
        self.printer.name = '<b>Printer</b>'
        self.printer.save()
        self.print.filename = '<i>file</i>.gcode'
        self.print.save()
        with patch('app.models.other_models.get_rotated_pic_url', return_value=None):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED)

        self.assertEqual(
            PrinterEvent.objects.get(print=self.print).event_text,
            '<div><i>Printer:</i> &lt;b&gt;Printer&lt;/b&gt;</div><div><i>G-Code:</i> &lt;i&gt;file&lt;/i&gt;.gcode</div>',
        )

    def test_event_create_allows_missing_snapshot(self):
        with patch('app.models.other_models.get_rotated_pic_url', return_value=None), \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.STARTED, task_handler=True)

        self.assertTrue(PrinterEvent.objects.filter(image_url=None, event_type=PrinterEvent.STARTED).exists())

    def test_new_print_start_allows_missing_snapshot(self):
        with patch('app.models.other_models.get_rotated_pic_url', return_value=None), \
                patch('app.models.other_models.celery_app'):
            self.printer.set_current_print('new.gcode', None, 2)

        self.assertTrue(PrinterEvent.objects.filter(print=self.printer.current_print, event_type=PrinterEvent.STARTED).exists())

    def test_rotated_pic_url_returns_none_when_source_is_missing_with_missing_ok(self):
        img_url = 'https://app.obico.io/ent/object_store/?t=1/tsd-pics/raw/1/2/3.jpg&d=x'
        response = Response()
        response.status_code = 404

        with patch.object(Printer, 'pic', new_callable=PropertyMock) as pic, \
                patch.object(Printer, 'settings', new_callable=PropertyMock) as settings, \
                patch('lib.utils.retrieve_to_file_obj', side_effect=HTTPError(response=response)), \
                patch('lib.utils.save_file_obj') as save_file_obj:
            pic.return_value = {'img_url': img_url}
            settings.return_value = {
                'webcam_flipV': True,
                'webcam_flipH': False,
                'webcam_rotation': 0,
            }

            self.assertIsNone(get_rotated_pic_url(self.printer, force_snapshot=True, missing_ok=True))

        save_file_obj.assert_not_called()

    def test_missing_ok_snapshot_preserves_rotation_behavior(self):
        img_url = 'https://app.obico.io/ent/object_store/?t=1/tsd-pics/raw/1/2/3.jpg&d=x'

        with patch.object(Printer, 'pic', new_callable=PropertyMock) as pic, \
                patch.object(Printer, 'settings', new_callable=PropertyMock) as settings, \
                patch('lib.utils.copy_pic', return_value='snapshot-url') as copy_pic:
            pic.return_value = {'img_url': img_url}
            settings.return_value = {
                'webcam_flipV': True,
                'webcam_flipH': False,
                'webcam_rotation': 0,
            }

            self.assertEqual(
                get_rotated_pic_url(self.printer, force_snapshot=True, missing_ok=True),
                'snapshot-url',
            )

        copy_pic.assert_called_once_with(
            'raw/1/2/3.jpg',
            ANY,
            syndicate_name=self.user.syndicate.name,
            rotated=True,
            printer_settings={
                'webcam_flipV': True,
                'webcam_flipH': False,
                'webcam_rotation': 0,
            },
            to_long_term_storage=False,
            missing_ok=True,
        )

    def test_print_progress_allows_missing_best_effort_snapshot(self):
        self.print.finished_at = None
        self.print.save()
        self.printer.current_print = self.print
        self.printer.save()
        MobileDevice.objects.create(
            user=self.user,
            platform='android',
            app_version='1',
            device_token='device-token',
        )

        with patch('lib.mobile_notifications.get_rotated_pic_url', return_value=None), \
                patch.object(Printer, 'not_watching_reason', return_value='not watching'), \
                patch('lib.mobile_notifications.cache.print_status_mobile_push_get', return_value=False), \
                patch('lib.mobile_notifications.cache.print_status_mobile_push_set'), \
                patch('lib.mobile_notifications.send_to_device') as send_to_device:
            mobile_notifications.send_print_progress(
                self.print,
                {'state': {'text': 'Printing'}, 'progress': {'completion': 1}},
            )

        self.assertEqual(send_to_device.call_args[0][0]['picUrl'], '')

    def test_get_rotated_pic_url_reads_cached_pic_once(self):
        img_url = 'https://app.obico.io/ent/object_store/?t=1/tsd-pics/snapshots/1/latest_unrotated.jpg&d=x'

        with patch.object(Printer, 'pic', new_callable=PropertyMock) as pic, \
                patch.object(Printer, 'settings', new_callable=PropertyMock) as settings:
            pic.side_effect = [{'img_url': img_url}, None]
            settings.return_value = {
                'webcam_flipV': False,
                'webcam_flipH': False,
                'webcam_rotation': 0,
            }

            self.assertEqual(get_rotated_pic_url(self.printer), img_url)


class ResignMediaUrlsCommandTestCase(TestCase):

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
        self.user = User.objects.create(email='resign@test.com', syndicate=syndicate)
        self.printer = Printer.objects.create(user=self.user)
        self.print = Print.objects.create(
            user=self.user,
            printer=self.printer,
            filename='test.gcode',
            ext_id=1,
            started_at=timezone.now(),
            finished_at=timezone.now(),
            video_url='http://old-host:3334/media/tsd-timelapses/private/1.mp4?digest=stale',
        )
        self.gcode_file = GCodeFile.objects.create(
            user=self.user,
            filename='test.gcode',
            safe_filename='test.gcode',
            url='/media/g_code_files/1.gcode?digest=stale',
        )
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.signed_with_path = os.path.join(tmp.name, '.media_urls_signed_with')
        signed_with = patch('app.management.commands.resign_media_urls.SIGNED_WITH_PATH', self.signed_with_path)
        signed_with.start()
        self.addCleanup(signed_with.stop)

    def test_urls_keep_their_host_and_get_valid_digest(self):
        call_command('resign_media_urls')

        self.print.refresh_from_db()
        self.assertTrue(self.print.video_url.startswith(
            'http://old-host:3334/media/tsd-timelapses/private/1.mp4?digest='))
        self.assertTrue(HmacSignedUrl(self.print.video_url).is_authorized())

        self.gcode_file.refresh_from_db()
        self.assertTrue(self.gcode_file.url.startswith('/media/g_code_files/1.gcode?digest='))
        self.assertTrue(HmacSignedUrl(self.gcode_file.url).is_authorized())


    def test_once_per_key_signs_only_after_the_key_changes(self):
        call_command('resign_media_urls', once_per_key=True)
        self.gcode_file.refresh_from_db()
        self.assertTrue(HmacSignedUrl(self.gcode_file.url).is_authorized())

        GCodeFile.objects.filter(id=self.gcode_file.id).update(url='/media/g_code_files/1.gcode?digest=stale')
        call_command('resign_media_urls', once_per_key=True)  # same key: nothing to do
        self.gcode_file.refresh_from_db()
        self.assertEqual(self.gcode_file.url, '/media/g_code_files/1.gcode?digest=stale')

        with override_settings(SECRET_KEY='a-rotated-key'):
            call_command('resign_media_urls', once_per_key=True)
            self.gcode_file.refresh_from_db()
            self.assertTrue(HmacSignedUrl(self.gcode_file.url).is_authorized())

    def test_addresses_outside_media_are_not_signed(self):
        planted = [
            'http://anything.example/media//etc/passwd',
            '/media/../../../etc/passwd',
            '/media/%2e%2e/%2e%2e/etc/passwd',
            'https://storage.example.com/bucket/1.gcode?sig=provider',
        ]
        files = [GCodeFile.objects.create(user=self.user, filename='p.gcode', safe_filename='p.gcode',
                                          url=url, thumbnail1_url=url) for url in planted]

        call_command('resign_media_urls')

        for gcode_file, url in zip(files, planted):
            gcode_file.refresh_from_db()
            self.assertEqual(gcode_file.url, url)
            self.assertEqual(gcode_file.thumbnail1_url, url)

    def test_file_on_a_printer_is_not_signed(self):
        # The agent stores its own path to the file; a /media/ path there was not written by the server.
        on_printer = GCodeFile.objects.create(
            user=self.user, filename='p.gcode', safe_filename='p.gcode', resident_printer=self.printer,
            url='/media/tsd-timelapses/private/1.mp4')

        call_command('resign_media_urls')

        on_printer.refresh_from_db()
        self.assertEqual(on_printer.url, '/media/tsd-timelapses/private/1.mp4')


class RewriteMediaUrlHostCommandTestCase(TestCase):

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
        self.user = User.objects.create(email='rewrite@test.com', syndicate=syndicate)
        self.printer = Printer.objects.create(user=self.user)
        self.print = Print.objects.create(
            user=self.user,
            printer=self.printer,
            filename='test.gcode',
            ext_id=1,
            started_at=timezone.now(),
            finished_at=timezone.now(),
            video_url=new_signed_url('http://old-host:3334/media/tsd-timelapses/private/1.mp4'),
            poster_url='https://storage.example.com/bucket/1.jpg?sig=provider',
        )
        self.gcode_file = GCodeFile.objects.create(
            user=self.user,
            filename='test.gcode',
            safe_filename='test.gcode',
            url=new_signed_url('/media/g_code_files/1.gcode'),
        )

    def test_matching_urls_are_rewritten_and_stay_valid(self):
        old_video_url = self.print.video_url

        call_command('rewrite_media_url_host', old_origin='http://old-host:3334', new_origin='https://new-host')

        self.print.refresh_from_db()
        self.assertEqual(self.print.video_url, old_video_url.replace('http://old-host:3334', 'https://new-host'))
        self.assertTrue(HmacSignedUrl(self.print.video_url).is_authorized())

    def test_other_origin_and_relative_urls_are_untouched(self):
        call_command('rewrite_media_url_host', old_origin='http://old-host:3334', new_origin='https://new-host')

        self.print.refresh_from_db()
        self.gcode_file.refresh_from_db()
        self.assertEqual(self.print.poster_url, 'https://storage.example.com/bucket/1.jpg?sig=provider')
        self.assertTrue(self.gcode_file.url.startswith('/media/g_code_files/1.gcode?digest='))

    def test_invalid_origin_is_rejected_before_touching_anything(self):
        old_video_url = self.print.video_url

        with self.assertRaises(CommandError):
            call_command('rewrite_media_url_host', old_origin='old-host:3334', new_origin='https://new-host')

        self.print.refresh_from_db()
        self.assertEqual(self.print.video_url, old_video_url)

    def test_dry_run_changes_nothing(self):
        old_video_url = self.print.video_url

        call_command('rewrite_media_url_host', old_origin='http://old-host:3334', new_origin='https://new-host', dry_run=True)

        self.print.refresh_from_db()
        self.assertEqual(self.print.video_url, old_video_url)


class PluginVersionSupportedTestCase(TestCase):
    """The tunnel only enforces a minimum version for Obico's own plugins."""

    def test_agents_without_a_minimum_version_are_supported(self):
        # Third-party agents report their own names and version formats.
        self.assertTrue(is_plugin_version_supported('Read-only Prusa cloud relay', '0.2.26-native-primary-status'))
        self.assertTrue(is_plugin_version_supported('PrusaLink read-only connector', '1.2.7'))

    def test_known_plugins_enforce_the_minimum_version(self):
        self.assertTrue(is_plugin_version_supported('octoprint_obico', '2.7.0'))
        self.assertFalse(is_plugin_version_supported('octoprint_obico', '1.8.3'))
        self.assertTrue(is_plugin_version_supported('moonraker_obico', '2.2.3'))
        self.assertFalse(is_plugin_version_supported('moonraker_obico', '1.2.0'))

    def test_known_plugin_with_an_unparseable_version_is_not_hidden(self):
        # Obico's own plugins always report a valid version, so this would be a real anomaly.
        with self.assertRaises(InvalidVersion):
            is_plugin_version_supported('octoprint_obico', 'not-a-version')


class TunnelPrinterCookiesTestCase(TestCase):
    """Cookies a printer sets through a tunnel stay on the tunnel's address."""

    def response_cookies(self, cookies):
        from app.models import OctoPrintTunnel
        from app.views import tunnelv2_views
        user, _ = User.objects.get_or_create(email='tunnel@example.com')
        tunnel = OctoPrintTunnel(id=1, printer=Printer(id=1, user=user), subdomain_code='abc123', app='App')
        reply = {'response': {'status': 200, 'headers': {}, 'content': b'', 'cookies': cookies}}
        with patch.object(tunnelv2_views.channels, 'send_msg_to_printer'), \
                patch.object(tunnelv2_views.cache, 'octoprinttunnel_http_response_get', return_value=reply):
            resp = tunnelv2_views._tunnel_http_req_and_wait_for_resp(tunnel, '/', 'GET', {}, b'', request_is_secure=True)
        return [v for k, v in resp.items() if k.lower() == 'set-cookie']

    def test_a_domain_attribute_is_removed(self):
        for cookie in ['tsd_sessionid=x; Domain=app.obico.io; Path=/', 'tsd_sessionid=x; path=/; domain =.obico.io',
                       'tsd_sessionid=x;Domain=app.obico.io']:
            [kept] = self.response_cookies([cookie])
            self.assertNotIn('domain', kept.lower(), cookie)
            self.assertTrue(kept.startswith('tsd_sessionid=x'))

    def test_cookies_without_a_domain_pass_unchanged(self):
        # Printer pages of any agent may use common names such as csrftoken.
        self.assertEqual(self.response_cookies(['csrftoken=t; Path=/; SameSite=Lax']),
                         ['csrftoken=t; Path=/; SameSite=Lax; Secure; Max-Age=7776000'])

    def test_octoprint_cookies_still_get_the_browser_port(self):
        self.assertEqual(self.response_cookies(['session_P80=s; Path=/; HttpOnly']), [
            'session_P443=s; Path=/; HttpOnly; Secure; Max-Age=7776000',
            'session_P80=s; Path=/; HttpOnly; Secure; Max-Age=7776000'])


@override_settings(SITE_ID=1, TUNNEL_DOMAIN='tun.example', OCTOPRINT_TUNNEL_PORT_RANGE=None)
class TunnelGzipTestCase(TestCase):
    """Tunnel responses are gzipped without a file name in the gzip header. Some apps (OctoApp)
    refuse gzip with a file name, which is where Django puts its BREACH padding."""

    GZIP_FLAGS_BYTE = 3
    GZIP_FNAME = 0x08

    def setUp(self):
        user = User.objects.create(email='tunnel-gzip@example.com')
        self.printer = Printer.objects.create(user=user, name='p', auth_token='tunnel-gzip-test-1', agent_version='2.7.2')
        self.content = b'{"state": "Operational", "temps": [' + b', '.join([b'210.0'] * 200) + b']}'

    def assert_gzipped_without_file_name(self, tunnel, host):
        import base64
        import gzip
        from app.views import tunnelv2_views
        auth = base64.b64encode(f'{tunnel.basicauth_username}:{tunnel.plain_basicauth_password}'.encode()).decode()
        reply = {'response': {'status': 200, 'headers': {'Content-Type': 'application/json'}, 'content': self.content}}
        with patch.object(tunnelv2_views.channels, 'num_ws_connections', return_value=1), \
                patch.object(tunnelv2_views.channels, 'send_msg_to_printer'), \
                patch.object(tunnelv2_views.cache, 'octoprinttunnel_http_response_get', return_value=reply):
            resp = Client(HTTP_HOST=host).get('/api/printer', HTTP_AUTHORIZATION=f'Basic {auth}', HTTP_ACCEPT_ENCODING='gzip')
        self.assertEqual((resp.status_code, resp['Content-Encoding']), (200, 'gzip'), host)
        self.assertFalse(resp.content[self.GZIP_FLAGS_BYTE] & self.GZIP_FNAME, host)
        self.assertEqual(gzip.decompress(resp.content), self.content, host)

    def test_tunnel_responses_have_no_file_name_in_the_gzip_header(self):
        from app.models import OctoPrintTunnel
        tunnel = OctoPrintTunnel.create(self.printer, app='Some App')
        site_domain = Site.objects.get(id=1).domain
        self.assert_gzipped_without_file_name(tunnel, f'{tunnel.subdomain_code}.tunnels.{site_domain}')
        self.assert_gzipped_without_file_name(tunnel, f'{tunnel.subdomain_code}.tun.example')

    @override_settings(TUNNEL_DOMAIN='', OCTOPRINT_TUNNEL_PORT_RANGE=range(4000, 4001))
    def test_tunnels_on_a_port_of_their_own_too(self):
        # How self-hosted servers run tunnels
        from app.models import OctoPrintTunnel
        tunnel = OctoPrintTunnel.create(self.printer, app='Some App')
        self.assert_gzipped_without_file_name(tunnel, 'localhost:4000')

    def test_other_pages_keep_the_random_padding(self):
        from django.http import HttpResponse
        from app.middleware import TSDGZipMiddleware
        request = RequestFactory().get('/', HTTP_ACCEPT_ENCODING='gzip')
        resp = TSDGZipMiddleware(lambda r: HttpResponse(self.content))(request)
        self.assertEqual(resp['Content-Encoding'], 'gzip')
        self.assertTrue(resp.content[self.GZIP_FLAGS_BYTE] & self.GZIP_FNAME)


@override_settings(SITE_ID=1, TUNNEL_DOMAIN='tun.example', OCTOPRINT_TUNNEL_PORT_RANGE=None)
class TunnelDomainTestCase(TestCase):
    """Tunnels on a domain of their own, which browsers treat as another site."""

    def setUp(self):
        from app.models import OctoPrintTunnel
        self.user = User.objects.create(email='tunnel-owner@example.com')
        self.user.set_password('first password')
        self.user.save()
        self.printer = Printer.objects.create(user=self.user, name='p', auth_token='tunnel-domain-test-1')
        self.tunnel = OctoPrintTunnel.get_or_create_for_internal_use(self.printer)
        self.host = f'{self.tunnel.subdomain_code}.tun.example'
        self.site_domain = Site.objects.get(id=1).domain
        self.old_host = f'{self.tunnel.subdomain_code}.tunnels.{self.site_domain}'
        self.app_tunnel = OctoPrintTunnel.create(self.printer, app='Some App')

    def sign_in_link(self, client=None):
        client = client or Client()
        client.force_login(self.user)
        resp = client.get(f'/octoprint/{self.printer.id}/')
        self.assertEqual(resp.status_code, 302)
        return resp['Location']

    def follow_sign_in(self, link, host=None, **headers):
        host = host or self.host
        prefix = f'http://{host}'
        self.assertTrue(link.startswith(prefix + '/_tsd_/signin/?token='), link)
        return Client(HTTP_HOST=host).get(link[len(prefix):], **headers)

    def tunnel_cookie(self, resp):
        from lib.tunnelv2 import TUNNEL_SESSION_COOKIE_NAME
        cookie = resp.cookies[TUNNEL_SESSION_COOKIE_NAME]
        self.assertEqual((cookie['httponly'], cookie['samesite'], cookie['domain']), (True, 'Lax', ''))
        return cookie.value

    def usage(self, cookie=None, host=None, **headers):
        from lib.tunnelv2 import TUNNEL_SESSION_COOKIE_NAME
        client = Client(HTTP_HOST=host or self.host)
        if cookie:
            client.cookies[TUNNEL_SESSION_COOKIE_NAME] = cookie
        return client.get('/_tsd_/tunnelusage/', **headers)

    def test_the_tunnel_address_is_on_the_tunnel_domain(self):
        self.assertTrue(self.tunnel.get_internal_tunnel_url(RequestFactory().get('/')).endswith(f'://{self.host}'))
        with override_settings(TUNNEL_DOMAIN=''):
            self.assertTrue(self.tunnel.get_internal_tunnel_url(RequestFactory().get('/')).endswith(f'://{self.old_host}'))

    def test_the_owner_is_signed_in_to_the_tunnel_with_a_one_time_link(self):
        link = self.sign_in_link()
        resp = self.follow_sign_in(link)
        self.assertEqual((resp.status_code, resp['Location']), (302, '/'))
        cookie = self.tunnel_cookie(resp)
        self.assertEqual(self.usage(cookie).status_code, 200)
        self.assertEqual(self.follow_sign_in(link).status_code, 401)

    def test_without_the_cookie_the_tunnel_is_closed(self):
        self.assertEqual(self.usage().status_code, 401)
        self.assertEqual(self.usage('forged').status_code, 401)

    def test_the_cookie_opens_only_its_own_tunnel(self):
        from app.models import OctoPrintTunnel
        cookie = self.tunnel_cookie(self.follow_sign_in(self.sign_in_link()))
        other_printer = Printer.objects.create(user=self.user, name='q', auth_token='tunnel-domain-test-2')
        other = OctoPrintTunnel.get_or_create_for_internal_use(other_printer)
        self.assertEqual(self.usage(cookie, host=f'{other.subdomain_code}.tun.example').status_code, 401)

    def test_a_password_change_closes_the_tunnel(self):
        cookie = self.tunnel_cookie(self.follow_sign_in(self.sign_in_link()))
        self.user.set_password('second password')
        self.user.save()
        self.assertEqual(self.usage(cookie).status_code, 401)

    def test_requests_from_another_tunnel_page_do_not_get_the_cookie(self):
        cookie = self.tunnel_cookie(self.follow_sign_in(self.sign_in_link()))
        self.assertEqual(self.usage(cookie, HTTP_SEC_FETCH_SITE='same-site', HTTP_SEC_FETCH_MODE='cors').status_code, 401)
        self.assertEqual(self.usage(cookie, HTTP_SEC_FETCH_SITE='same-origin', HTTP_SEC_FETCH_MODE='cors').status_code, 200)
        # Following a link from another site to the tunnel still works
        self.assertEqual(self.usage(cookie, HTTP_SEC_FETCH_SITE='cross-site', HTTP_SEC_FETCH_MODE='navigate').status_code, 200)

    def test_websockets_from_another_page_do_not_get_the_cookie(self):
        from lib.tunnelv2 import OctoprintTunnelV2Helper, TunnelAuthenticationError, TUNNEL_SESSION_COOKIE_NAME
        cookie = self.tunnel_cookie(self.follow_sign_in(self.sign_in_link()))

        def scope(origin):
            return {'headers': [(b'host', self.host.encode()), (b'origin', origin.encode())],
                    'cookies': {TUNNEL_SESSION_COOKIE_NAME: cookie}, 'user': AnonymousUser()}

        self.assertEqual(OctoprintTunnelV2Helper.get_octoprinttunnel(scope(f'https://{self.host}')), self.tunnel)
        for origin in ('https://other.tun.example', 'https://app.example'):
            with self.assertRaises(TunnelAuthenticationError):
                OctoprintTunnelV2Helper.get_octoprinttunnel(scope(origin))

    def test_a_page_on_an_old_address_moves_to_the_tunnel_domain(self):
        client = Client(HTTP_HOST=self.old_host)
        client.force_login(self.user)
        resp = client.get('/some/page?x=1', HTTP_SEC_FETCH_DEST='iframe')
        self.assertEqual(resp.status_code, 302)
        signed_in = self.follow_sign_in(resp['Location'])
        self.assertEqual(signed_in['Location'], '/some/page?x=1')


    def test_an_app_page_opened_with_its_password_on_an_old_address_needs_no_password_again(self):
        import base64
        old_app_host = f'{self.app_tunnel.subdomain_code}.tunnels.{self.site_domain}'
        new_app_host = f'{self.app_tunnel.subdomain_code}.tun.example'

        def basic(password):
            return 'Basic ' + base64.b64encode(f'{self.app_tunnel.basicauth_username}:{password}'.encode()).decode()

        # Browsers send the password from the link only when asked for it
        for headers in ({}, {'HTTP_AUTHORIZATION': basic('wrong')}):
            asked = Client(HTTP_HOST=old_app_host).get('/some/page', HTTP_SEC_FETCH_DEST='document', **headers)
            self.assertEqual(asked.status_code, 401)
            self.assertTrue(asked['WWW-Authenticate'].startswith('Basic realm='))

        resp = Client(HTTP_HOST=old_app_host).get(
            '/some/page?x=1', HTTP_SEC_FETCH_DEST='document',
            HTTP_AUTHORIZATION=basic(self.app_tunnel.plain_basicauth_password))
        self.assertEqual(resp.status_code, 302)
        signed_in = self.follow_sign_in(resp['Location'], host=new_app_host)
        self.assertEqual(signed_in['Location'], '/some/page?x=1')
        cookie = self.tunnel_cookie(signed_in)
        self.assertEqual(self.usage(cookie, host=new_app_host).status_code, 200)
        # Good for this app's tunnel only
        self.assertEqual(self.usage(cookie).status_code, 401)
        self.app_tunnel.delete()
        self.assertEqual(self.usage(cookie, host=new_app_host).status_code, 401)

    def test_apps_keep_using_old_addresses(self):
        import base64
        app_host = f'{self.app_tunnel.subdomain_code}.tunnels.{self.site_domain}'
        auth = base64.b64encode(f'{self.app_tunnel.basicauth_username}:{self.app_tunnel.plain_basicauth_password}'.encode()).decode()
        self.assertEqual(self.usage(host=app_host, HTTP_AUTHORIZATION=f'Basic {auth}').status_code, 200)
        client = Client(HTTP_HOST=self.old_host)
        client.force_login(self.user)
        self.assertEqual(client.get('/_tsd_/tunnelusage/').status_code, 200)

    @override_settings(TUNNEL_DOMAIN='')
    def test_without_a_tunnel_domain_nothing_changes(self):
        client = Client()
        client.force_login(self.user)
        self.assertEqual(client.get(f'/octoprint/{self.printer.id}/')['Location'], f'http://{self.old_host}')
        client = Client(HTTP_HOST=self.old_host)
        client.force_login(self.user)
        self.assertEqual(client.get('/_tsd_/tunnelusage/', HTTP_SEC_FETCH_DEST='document').status_code, 200)

    def test_an_offline_cache_on_the_tunnel_domain_is_replaced_by_one_that_removes_itself(self):
        # Fluidd's and Mainsail's cache would otherwise answer the sign-in link with a blank page
        from app.views import tunnelv2_views
        with patch.object(tunnelv2_views.channels, 'send_msg_to_printer') as to_printer:
            resp = Client(HTTP_HOST=self.host).get('/sw.js', HTTP_SERVICE_WORKER='script')
        self.assertEqual((resp.status_code, resp['Content-Type'], resp['Cache-Control']),
                         (200, 'text/javascript', 'no-store'))
        self.assertIn(b'self.registration.unregister()', resp.content)
        to_printer.assert_not_called()

    def test_a_used_sign_in_link_reloaded_by_a_signed_in_browser_opens_the_tunnel(self):
        # A page stuck on an offline cache sends the link once, then reloads it
        link = self.sign_in_link()
        cookie = self.tunnel_cookie(self.follow_sign_in(link))
        from lib.tunnelv2 import TUNNEL_SESSION_COOKIE_NAME
        client = Client(HTTP_HOST=self.host)
        client.cookies[TUNNEL_SESSION_COOKIE_NAME] = cookie
        resp = client.get(link[len(f'http://{self.host}'):])
        self.assertEqual((resp.status_code, resp['Location']), (302, '/'))
        # A cookie of another tunnel does not count
        other_printer = Printer.objects.create(user=self.user, name='q', auth_token='tunnel-domain-test-3')
        from app.models import OctoPrintTunnel
        other = OctoPrintTunnel.get_or_create_for_internal_use(other_printer)
        client = Client(HTTP_HOST=f'{other.subdomain_code}.tun.example')
        client.cookies[TUNNEL_SESSION_COOKIE_NAME] = cookie
        self.assertEqual(client.get('/_tsd_/signin/?token=used').status_code, 401)

    def forwarded_headers(self, agent_name, path):
        from lib.tunnelv2 import TUNNEL_SESSION_COOKIE_NAME
        from app.views import tunnelv2_views
        self.printer.agent_name, self.printer.agent_version = agent_name, '2.7.2'
        self.printer.save()
        cookie = self.tunnel_cookie(self.follow_sign_in(self.sign_in_link()))
        client = Client(HTTP_HOST=self.host)
        client.cookies[TUNNEL_SESSION_COOKIE_NAME] = cookie
        reply = {'response': {'status': 200, 'headers': {}, 'content': b'{}'}}
        with patch.object(tunnelv2_views.channels, 'num_ws_connections', return_value=1), \
                patch.object(tunnelv2_views.channels, 'send_msg_to_printer') as to_printer, \
                patch.object(tunnelv2_views.cache, 'octoprinttunnel_http_response_get', return_value=reply):
            client.get(path, HTTP_IF_NONE_MATCH='"abc"', HTTP_IF_MODIFIED_SINCE='Thu, 01 Jan 2026 00:00:00 GMT')
        return to_printer.call_args[0][1]['http.tunnelv2']['headers']

    def test_klipper_printers_are_asked_for_the_whole_config_json(self):
        # Obico for Klipper answers 502 to an empty "not modified" config.json; Fluidd goes blank
        headers = self.forwarded_headers('moonraker_obico', '/config.json')
        self.assertNotIn('If-None-Match', headers)
        self.assertNotIn('If-Modified-Since', headers)
        for agent, path in (('moonraker_obico', '/index.html'), ('octoprint_obico', '/config.json')):
            self.assertEqual(self.forwarded_headers(agent, path)['If-None-Match'], '"abc"', (agent, path))

    def test_other_scripts_on_the_tunnel_domain_still_need_the_sign_in(self):
        self.assertEqual(Client(HTTP_HOST=self.host).get('/sw.js').status_code, 401)

    def test_offline_caches_elsewhere_are_left_alone(self):
        # An old address, or a server without a tunnel domain (as self-hosted servers run)
        self.assertEqual(Client(HTTP_HOST=self.old_host).get('/sw.js', HTTP_SERVICE_WORKER='script').status_code, 401)
        with override_settings(TUNNEL_DOMAIN=''):
            self.assertEqual(Client(HTTP_HOST=self.old_host).get('/sw.js', HTTP_SERVICE_WORKER='script').status_code, 401)

    def test_the_tunnel_cookie_is_not_sent_to_the_printer(self):
        from app.views.tunnelv2_views import DJANGO_COOKIE_RE
        self.assertTrue(DJANGO_COOKIE_RE.match('tsd_tunnel_session=x'))


class GCodeThumbnailParseTestCase(TestCase):
    """lib.gcode_metadata.parse reads the thumbnail files that the moonraker parser writes."""

    @staticmethod
    def thumbnail_block(width, height):
        import base64, io
        from PIL import Image
        buf = io.BytesIO()
        Image.new('RGB', (width, height), 'red').save(buf, 'PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        lines = ''.join(f'; {b64[i:i + 78]}\n' for i in range(0, len(b64), 78))
        return f'; thumbnail begin {width}x{height} {len(b64)}\n{lines}; thumbnail end\n'

    def parse(self, *blocks):
        import io
        from lib import gcode_metadata
        data = ('; generated by PrusaSlicer 2.7.0 on 2026-01-01 at 00:00:00 UTC\n'
                + ''.join(blocks) + 'G28\nG1 X10 Y10 E1\n').encode()
        return gcode_metadata.parse(io.BytesIO(data), len(data), 'utf-8')

    def test_two_thumbnails_of_different_sizes_are_both_returned(self):
        _, thumbnails = self.parse(self.thumbnail_block(160, 160), self.thumbnail_block(48, 48))

        self.assertEqual(len(thumbnails), 3)  # 160x160, 48x48 and the generated 32x32

    def test_two_thumbnails_of_the_same_size_do_not_read_a_deleted_file(self):
        _, thumbnails = self.parse(self.thumbnail_block(160, 160), self.thumbnail_block(160, 160))

        self.assertEqual(len(thumbnails), 2)  # 160x160 once, plus the generated 32x32


class AccountAdapterClientIpTestCase(SimpleTestCase):
    """allauth counts its rate limits per client IP, read like every other
    client address: X-Forwarded-For counted back NUM_TRUSTED_PROXIES entries."""

    def client_ip(self, proxies, **meta):
        from django.test import override_settings
        from rest_framework.settings import api_settings
        with override_settings(REST_FRAMEWORK={'NUM_PROXIES': proxies}):
            api_settings.reload()
            request = RequestFactory().get('/', **meta)
            try:
                return SyndicateSpecificAccountAdapter(request).get_client_ip(request)
            finally:
                api_settings.reload()

    def test_without_a_proxy_the_header_is_ignored(self):
        self.assertEqual(self.client_ip(0, HTTP_X_FORWARDED_FOR='203.0.113.9', REMOTE_ADDR='198.51.100.4'), '198.51.100.4')

    def test_behind_one_proxy(self):
        self.assertEqual(
            self.client_ip(1, HTTP_X_FORWARDED_FOR='203.0.113.9, 198.51.100.4', REMOTE_ADDR='10.0.0.2'),
            '198.51.100.4')

    def test_behind_a_google_load_balancer(self):
        # It keeps what the client wrote and appends the client and itself.
        self.assertEqual(
            self.client_ip(2, HTTP_X_FORWARDED_FOR='203.0.113.9, 198.51.100.4, 34.95.90.112', REMOTE_ADDR='35.191.0.1'),
            '198.51.100.4')


class EmailLookupBySyndicateTestCase(TestCase):
    """Every lookup of an account by address (EmailAddress rows and User.email)
    keeps to one syndicate."""

    def setUp(self):
        self.base, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        self.other, _ = Syndicate.objects.get_or_create(id=2, defaults={'name': 'yumi'})
        self.site, _ = Site.objects.get_or_create(domain='testserver', defaults={'name': 'testserver'})
        SiteSyndicate.objects.update_or_create(site=self.site, defaults={'syndicate': self.base})

    def user(self, email, syndicate, password=None):
        user = User.objects.create(email=email, username=f'{email}_{syndicate.id}', syndicate=syndicate)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def test_finds_both_records_in_one_syndicate_only(self):
        no_rows = self.user('a@example.com', self.base)  # User.email only
        second = self.user('b@example.com', self.base)
        EmailAddress.objects.create(user=second, email='b2@example.com')
        elsewhere = self.user('a@example.com', self.other)
        self.assertEqual(users_by_email('A@example.com', self.base), [no_rows])
        self.assertEqual(users_by_email('b2@example.com', self.base), [second])
        self.assertEqual(users_by_email('a@example.com', self.other), [elsewhere])

    def test_an_account_with_both_records_is_found_once(self):
        user = self.user('a@example.com', self.base)
        EmailAddress.objects.create(user=user, email='a@example.com', primary=True)
        self.assertEqual(users_by_email('a@example.com', self.base), [user])

    def test_a_verified_address_in_another_syndicate_hides_nothing(self):
        verified_elsewhere = self.user('a@example.com', self.other)
        EmailAddress.objects.create(user=verified_elsewhere, email='a@example.com', verified=True, primary=True)
        unverified = self.user('a@example.com', self.base)
        EmailAddress.objects.create(user=unverified, email='a@example.com', primary=True)
        self.assertEqual(users_by_email('a@example.com', self.base), [unverified])

    def test_inactive_accounts(self):
        user = self.user('a@example.com', self.base)
        user.is_active = False
        user.save()
        self.assertEqual(users_by_email('a@example.com', self.base), [user])
        self.assertEqual(users_by_email('a@example.com', self.base, is_active=True), [])

    def reset_form(self, email, **meta):
        request = RequestFactory().post('/', **meta)
        request.user = AnonymousUser()
        request.site = self.site
        return SyndicateSpecificResetPasswordForm(data={'email': email}, request=request)

    def test_password_reset_follows_the_syndicate_header(self):
        user = self.user('y@example.com', self.other, password='correct horse')
        self.assertFalse(self.reset_form('y@example.com').is_valid())
        form = self.reset_form('y@example.com', HTTP_X_OBICO_SYNDICATE='yumi')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.users, [user])

    def test_password_reset_finds_an_account_without_address_rows(self):
        user = self.user('a@example.com', self.base, password='correct horse')
        form = self.reset_form('a@example.com')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.users, [user])

    def test_an_address_that_only_upper_cases_the_same_is_another_address(self):
        # The upper case of "ı" (dotless i) is "I", so the database's
        # case-insensitive match finds these accounts. "example.ınvalıd" is
        # another domain, and mail would go to the typed address.
        user = self.user('a@example.invalid', self.base, password='correct horse')
        EmailAddress.objects.create(user=user, email='b@example.invalid', primary=True)
        for look_alike in ('a@example.ınvalıd', 'b@example.ınvalıd'):
            self.assertEqual(users_by_email(look_alike, self.base), [])
            self.assertFalse(self.reset_form(look_alike).is_valid())
        self.assertEqual(users_by_email('A@EXAMPLE.INVALID', self.base), [user])
        self.assertEqual(users_by_email('B@example.invalid', self.base), [user])


class UnsubscribeEmailTestCase(TestCase):
    """The unsubscribe link in notification emails. A person clicks it in the
    email body (GET); Gmail's one-click unsubscribe (RFC 8058) POSTs
    'List-Unsubscribe=One-Click' to the same URL, with no CSRF token."""

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        site, _ = Site.objects.get_or_create(domain='testserver', defaults={'name': 'testserver'})
        SiteSyndicate.objects.update_or_create(site=site, defaults={'syndicate': syndicate})
        # Django caches the site per host; another test's rolled-back site would linger.
        Site.objects.clear_cache()
        self.addCleanup(Site.objects.clear_cache)
        self.user = User.objects.create(email='unsub@example.com', syndicate=syndicate)
        self.nsetting = NotificationSetting.objects.get(user=self.user, name='email')
        self.client = Client(enforce_csrf_checks=True)

    def url(self, unsub_token, email_list='print_done'):
        return f'/unsubscribe_email/?unsub_token={unsub_token}&list={email_list}'

    def test_link_click_turns_the_setting_off(self):
        response = self.client.get(self.url(self.user.unsub_token))
        self.assertEqual(response.status_code, 200)
        self.nsetting.refresh_from_db()
        self.assertFalse(self.nsetting.notify_on_print_done)

    def test_one_click_post_turns_the_setting_off(self):
        response = self.client.post(
            self.url(self.user.unsub_token),
            data='List-Unsubscribe=One-Click',
            content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.nsetting.refresh_from_db()
        self.assertFalse(self.nsetting.notify_on_print_done)

    def test_one_click_post_turns_account_notifications_off(self):
        response = self.client.post(
            self.url(self.user.unsub_token, 'account_notification'),
            data='List-Unsubscribe=One-Click',
            content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.account_notification_by_email)

    def test_an_unknown_token_is_not_found(self):
        for response in (
            self.client.get(self.url(uuid.uuid4())),
            self.client.post(
                self.url(uuid.uuid4()),
                data='List-Unsubscribe=One-Click',
                content_type='application/x-www-form-urlencoded'),
        ):
            self.assertEqual(response.status_code, 404)
        self.nsetting.refresh_from_db()
        self.assertTrue(self.nsetting.notify_on_print_done)


class SiteSyndicateTestCase(TestCase):
    """Each site serves one syndicate."""

    def setUp(self):
        self.base, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        self.other, _ = Syndicate.objects.get_or_create(id=2, defaults={'name': 'yumi'})

    def test_a_new_site_serves_the_first_syndicate(self):
        site = Site.objects.create(domain='192.168.1.5:3334', name='mine')
        self.assertEqual(site.site_syndicate.syndicate, self.base)

    def test_a_site_added_in_django_admin(self):
        # The self-hosting guide's way (website/docs/server-guides/configure.md).
        admin = User.objects.create_superuser(email='site-admin@example.com', password='supersecret')
        self.client.force_login(admin)
        response = self.client.post('/admin/sites/site/add/', {'domain': '192.168.1.5:3334', 'name': 'mine'})
        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(Site.objects.get(domain='192.168.1.5:3334').site_syndicate.syndicate, self.base)

    def test_links_use_the_syndicates_first_site_by_domain(self):
        for domain in ('example.com', 'localhost:3334', '192.168.1.5:3334'):
            site, _ = Site.objects.get_or_create(domain=domain, defaults={'name': domain})
            SiteSyndicate.objects.update_or_create(site=site, defaults={'syndicate': self.other})
        syndicate_lib.SYNDICATE_DOMAIN_CACHE.clear()
        self.addCleanup(syndicate_lib.SYNDICATE_DOMAIN_CACHE.clear)
        self.assertTrue(syndicate_lib.build_full_url_for_syndicate('/printers/', 'yumi').endswith(
            '://192.168.1.5:3334/printers/'))


@override_settings(EMAIL_HOST='smtp.example.com')
class SendTestEmailAdminActionTestCase(TestCase):
    """The "Send test email" action on Django admin's user list. Only sign-up
    creates the EmailAddress rows email is sent to, so an account created in
    Django admin, like the default root@example.com, has none."""

    def setUp(self):
        # Seeded by migration 0002, as on every new server.
        self.admin = User.objects.get(email='root@example.com')
        self.client.force_login(self.admin)

    def send_test_email(self, *users):
        return self.client.post('/admin/app/user/', {
            'action': 'send_test_email',
            '_selected_action': [u.id for u in users],
        }, follow=True)

    def test_an_account_with_no_address_is_told_it_cannot_receive_one(self):
        response = self.send_test_email(self.admin)
        self.assertEqual(len(mail.outbox), 0)
        sent = list(response.context['messages'])
        self.assertEqual([m.level for m in sent], [messages.ERROR])
        self.assertIn('root@example.com', sent[0].message)
        self.assertIn('created in Django admin', sent[0].message)

    def test_an_account_that_signed_up_gets_one(self):
        signed_up = User.objects.create(email='signed-up@example.com', syndicate_id=1)
        EmailAddress.objects.create(user=signed_up, email=signed_up.email, primary=True)
        response = self.send_test_email(self.admin, signed_up)
        self.assertEqual([m.to for m in mail.outbox], [['signed-up@example.com']])
        self.assertEqual(sorted(m.level for m in response.context['messages']), [messages.SUCCESS, messages.ERROR])


class SiteSyndicateMigrationTestCase(TransactionTestCase):
    """Migration 0086, from the many-to-many link to one syndicate per site.
    Outside a transaction, because SQLite, the self-hosted default, cannot
    change its schema inside one. serialized_rollback puts back the rows the
    migrations created, and tearDown the latest schema, for the tests after it."""
    before = [('app', '0085_printerprediction_normalized_p')]
    after = [('app', '0086_sitesyndicate')]
    serialized_rollback = True

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_each_site_keeps_its_first_syndicate_and_an_unlinked_one_gets_the_first(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.before)
        apps = executor.loader.project_state(self.before).apps
        Site, Syndicate_ = apps.get_model('sites', 'Site'), apps.get_model('app', 'Syndicate')
        base = Syndicate_.objects.order_by('id').first()
        # base was inserted with id 1 by a migration that left the id sequence behind.
        other = Syndicate_.objects.create(id=Syndicate_.objects.order_by('-id').first().id + 1, name='kingroon')
        both = Site.objects.create(domain='both.example.com', name='both')
        base.sites.add(both)
        other.sites.add(both)
        theirs = Site.objects.create(domain='theirs.example.com', name='theirs')
        other.sites.add(theirs)
        unlinked = Site.objects.create(domain='unlinked.example.com', name='unlinked')

        executor = MigrationExecutor(connection)
        executor.migrate(self.after)
        apps = executor.loader.project_state(self.after).apps
        links = dict(apps.get_model('app', 'SiteSyndicate').objects.values_list('site_id', 'syndicate_id'))
        self.assertEqual(links[both.id], base.id)
        self.assertEqual(links[theirs.id], other.id)
        self.assertEqual(links[unlinked.id], base.id)
        self.assertEqual(set(links), set(Site.objects.values_list('id', flat=True)))


class ServeMediaFileTestCase(TestCase):
    """A signed /media/ link serves only files inside MEDIA_ROOT."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.media_root = os.path.join(tmp.name, 'media')
        os.makedirs(os.path.join(self.media_root, 'tsd-timelapses'))
        with open(os.path.join(self.media_root, 'tsd-timelapses', '1.jpg'), 'wb') as f:
            f.write(b'snapshot')
        with open(os.path.join(tmp.name, 'outside.txt'), 'wb') as f:
            f.write(b'outside')
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)

    def get(self, path):
        return Client().get(new_signed_url(path))

    def test_signed_link_to_a_media_file_is_served(self):
        response = self.get('/media/tsd-timelapses/1.jpg')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'snapshot')

    def test_wrong_digest_is_refused(self):
        response = Client().get('/media/tsd-timelapses/1.jpg?digest=wrong')

        self.assertEqual(response.status_code, 403)

    def test_signed_link_outside_media_root_is_refused(self):
        for path in ('/media/../outside.txt', '/media/tsd-timelapses/../../outside.txt', '/media/' + self.media_root + '/../outside.txt'):
            with self.subTest(path=path):
                self.assertEqual(self.get(path).status_code, 400)


class SecretKeyFromFileTestCase(SimpleTestCase):
    """Without DJANGO_SECRET_KEY, the server generates a key once and keeps it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.path = os.path.join(tmp.name, '.django_secret_key')

    def test_first_start_generates_a_private_key_and_later_starts_reuse_it(self):
        from config.settings import secret_key_from_file

        key = secret_key_from_file(self.path)

        self.assertGreaterEqual(len(key), 50)
        self.assertEqual(os.stat(self.path).st_mode & 0o777, 0o600)
        self.assertEqual(secret_key_from_file(self.path), key)
        self.assertEqual(os.listdir(self.dir), ['.django_secret_key'])

    def test_a_process_starting_at_the_same_time_uses_the_key_saved_first(self):
        from config.settings import secret_key_from_file
        with open(self.path, 'w') as f:
            f.write('saved-by-the-other-process')

        # This process checked before the other one saved its key.
        with patch('os.path.exists', return_value=False):
            key = secret_key_from_file(self.path)

        self.assertEqual(key, 'saved-by-the-other-process')
        self.assertEqual(os.listdir(self.dir), ['.django_secret_key'])


class OAuthApplicationRegistrationTestCase(TestCase):
    """Only staff register and manage OAuth applications; everyone else keeps the
    authorization flow and the list of apps they authorized."""

    def setUp(self):
        from oauth2_provider.models import Application
        self.member = User.objects.create(email='member@example.com')
        self.staff = User.objects.create(email='staff@example.com', is_staff=True)
        self.app = Application.objects.create(
            name='Staff App', user=self.staff, client_type='confidential',
            authorization_grant_type='authorization-code', redirect_uris='https://app.example/cb')

    def client_for(self, user=None):
        client = Client()
        if user:
            client.force_login(user)
        return client

    def test_a_member_cannot_register_or_manage_applications(self):
        from oauth2_provider.models import Application
        client = self.client_for(self.member)
        resp = client.post('/o/applications/register/', {
            'name': 'Obico', 'client_type': 'confidential',
            'authorization_grant_type': 'authorization-code', 'redirect_uris': 'https://attacker.example/cb'})
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Application.objects.filter(name='Obico').exists())
        for path in ['/o/applications/', '/o/applications/register/', f'/o/applications/{self.app.id}/',
                     f'/o/applications/{self.app.id}/update/', f'/o/applications/{self.app.id}/delete/']:
            self.assertEqual(client.get(path).status_code, 403, path)

    def test_a_signed_out_visitor_cannot_reach_the_application_pages(self):
        self.assertEqual(self.client_for().get('/o/applications/register/').status_code, 403)

    def test_staff_can_register_an_application(self):
        from oauth2_provider.models import Application
        resp = self.client_for(self.staff).post('/o/applications/register/', {
            'name': 'New App', 'client_id': 'new-app-id', 'client_secret': 'new-app-secret',
            'hash_client_secret': 'on', 'client_type': 'confidential',
            'authorization_grant_type': 'authorization-code', 'redirect_uris': 'https://new.example/cb',
            'post_logout_redirect_uris': '', 'allowed_origins': '', 'algorithm': ''})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Application.objects.filter(name='New App', user=self.staff).exists())

    def test_a_member_still_authorizes_apps_and_sees_the_ones_authorized(self):
        client = self.client_for(self.member)
        resp = client.get('/o/authorize/', {
            'response_type': 'code', 'client_id': self.app.client_id,
            'redirect_uri': 'https://app.example/cb', 'scope': 'read'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Staff App')
        self.assertEqual(client.get('/o/authorized_tokens/').status_code, 200)


class XApiKeyIsNotASignInTestCase(TestCase):
    """An OAuth token works only as a Bearer token on the API; in an X-Api-Key
    header it signs nobody in to the site's pages."""

    def setUp(self):
        import datetime
        from oauth2_provider.models import AccessToken, Application
        self.user = User.objects.create(email='token-owner@example.com')
        self.user.set_unusable_password()  # as after a Google, Apple or emailed-code sign-up
        self.user.save()
        app = Application.objects.create(
            name='Some App', client_type='confidential',
            authorization_grant_type='authorization-code', redirect_uris='https://app.example/cb')
        self.token = AccessToken.objects.create(
            user=self.user, application=app, token='x-api-key-test-token', scope='read',
            expires=timezone.now() + datetime.timedelta(days=1)).token

    def test_a_token_in_x_api_key_opens_no_signed_in_page(self):
        for path in ['/accounts/email/', '/accounts/password/set/', '/user_preferences/']:
            resp = Client().get(path, HTTP_X_API_KEY=self.token)
            self.assertEqual(resp.status_code, 302, path)
            self.assertTrue(resp['Location'].startswith('/accounts/login/'), path)

    def test_a_token_in_x_api_key_sets_no_password(self):
        Client().post('/accounts/password/set/', {'password1': 'A-new-password-1', 'password2': 'A-new-password-1'},
                      HTTP_X_API_KEY=self.token)
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_usable_password())

    def test_the_same_token_still_works_as_a_bearer_token_on_the_api(self):
        resp = Client().get('/api/v1/printers/', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(resp.status_code, 200)


# The views an OAuth token reaches: the API for apps in website/docs/api/.
# Adding one here opens it to every app a user has authorized.
OAUTH_TOKEN_VIEWS = {
    'api.viewsets.ApiVersionView',
    'api.viewsets.GCodeFileViewSet',
    'api.viewsets.GCodeFolderViewSet',
    'api.viewsets.PrintViewSet',
    'api.viewsets.PrinterViewSet',
    'app.jusprin.views.JusPrinChatViewSet',
    'app.jusprin.views.JusPrinContactSupportRequestViewSet',
    'app.jusprin.views.JusPrinMeViewSet',
    'app.jusprin.views.JusPrinPlateAnalysisViewSet',
}


def _view_classes(patterns):
    from django.urls import URLPattern, URLResolver
    for p in patterns:
        if isinstance(p, URLResolver):
            yield from _view_classes(p.url_patterns)
        elif isinstance(p, URLPattern):
            view = getattr(p.callback, 'cls', None) or getattr(p.callback, 'view_class', None)
            if view is not None:
                yield view


class OAuthTokenViewsTestCase(SimpleTestCase):
    """Every view of this project that takes OAuth tokens takes them through
    ScopedOAuth2Authentication, and only the listed views declare scopes."""

    def views(self):
        from django.urls import get_resolver
        return {v for v in _view_classes(get_resolver().url_patterns) if v.__module__.split('.')[0] in ('api', 'app')}

    def test_no_view_takes_tokens_without_the_scope_rule(self):
        from oauth2_provider.contrib.rest_framework import OAuth2Authentication
        from api.authentication import ScopedOAuth2Authentication
        for view in self.views():
            for auth in getattr(view, 'authentication_classes', ()):
                if issubclass(auth, OAuth2Authentication):
                    self.assertIs(auth, ScopedOAuth2Authentication, f'{view.__module__}.{view.__name__}')

    def test_only_the_api_for_apps_declares_scopes(self):
        declared = {f'{v.__module__}.{v.__name__}' for v in self.views() if hasattr(v, 'required_scopes')}
        self.assertEqual(declared, OAUTH_TOKEN_VIEWS)


class OAuthTokenScopeTestCase(TestCase):
    """A token reaches only the API for apps, needs `read` to read and `write`
    to change anything there, and never becomes a browser session."""

    def setUp(self):
        import datetime
        from oauth2_provider.models import AccessToken, Application
        self.user = User.objects.create(email='scoped-token-owner@example.com')
        self.gcode = GCodeFile.objects.create(user=self.user, filename='part.gcode', safe_filename='part.gcode')
        app = Application.objects.create(
            name='Some App', client_type='confidential',
            authorization_grant_type='authorization-code', redirect_uris='https://app.example/cb')

        def token(scope):
            return AccessToken.objects.create(
                user=self.user, application=app, token=f'scoped-{scope.replace(" ", "-")}', scope=scope,
                expires=timezone.now() + datetime.timedelta(days=1)).token
        self.read, self.read_write = token('read'), token('read write')

    def call(self, method, path, token, data=None):
        return getattr(Client(), method)(path, data, content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_a_read_token_reads_but_changes_nothing(self):
        self.assertEqual(self.call('get', '/api/v1/g_code_files/', self.read).status_code, 200)
        resp = self.call('patch', f'/api/v1/g_code_files/{self.gcode.id}/', self.read, {'filename': 'renamed.gcode'})
        self.assertEqual(resp.status_code, 403)
        self.gcode.refresh_from_db()
        self.assertEqual(self.gcode.filename, 'part.gcode')

    def test_a_write_token_changes_the_api_for_apps(self):
        resp = self.call('patch', f'/api/v1/g_code_files/{self.gcode.id}/', self.read_write, {'filename': 'renamed.gcode'})
        self.assertEqual(resp.status_code, 200)

    def test_a_token_is_no_sign_in_outside_the_api_for_apps(self):
        for method, path in [('get', '/api/v1/users/me/'), ('patch', '/api/v1/users/me/'),
                             ('get', '/api/v1/notification_settings/'), ('post', '/api/v1/mobile_devices/'),
                             ('post', '/api/v1/tunnels/'), ('get', '/api/v1/printer_events/')]:
            self.assertEqual(self.call(method, path, self.read_write, {}).status_code, 403, path)

    def test_a_browser_session_is_not_affected(self):
        client = Client()
        client.force_login(self.user, backend='app.accounts.SyndicateSpecificBackend')
        self.assertEqual(client.get('/api/v1/users/me/').status_code, 200)

    def test_a_token_does_not_turn_a_failed_sign_in_into_a_session(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        site, _ = Site.objects.get_or_create(domain='testserver', defaults={'name': 'testserver'})
        SiteSyndicate.objects.update_or_create(site=site, defaults={'syndicate': syndicate})
        # Django caches the site per host; another test's rolled-back site would linger.
        Site.objects.clear_cache()
        self.addCleanup(Site.objects.clear_cache)
        client = Client()
        resp = client.post('/accounts/login/', {'login': 'nobody@example.invalid', 'password': 'wrong-password-1'},
                           HTTP_AUTHORIZATION=f'Bearer {self.read}')
        self.assertNotEqual(resp.status_code, 302)
        self.assertIsNone(client.session.get('_auth_user_id'))
        self.assertEqual(client.get('/api/v1/users/me/').status_code, 403)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SignupTestCase(TestCase):
    """Sign-up on the web and in the mobile apps: reCAPTCHA when the server has
    a key, and the password rules."""

    PASSWORD = 'violet-harbor-1847'

    def setUp(self):
        self.base, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        self.site, _ = Site.objects.get_or_create(domain='testserver', defaults={'name': 'testserver'})
        SiteSyndicate.objects.update_or_create(site=self.site, defaults={'syndicate': self.base})
        # Django caches the site per host; another test's rolled-back site would linger.
        Site.objects.clear_cache()
        self.addCleanup(Site.objects.clear_cache)

    def sign_up(self, email, password, **extra):
        return Client().post('/mobile/auth/signup/', {
            'email': email, 'password1': password, 'password2': password, **extra})

    def created(self, email):
        return User.objects.filter(email=email).exists()

    @override_settings(RECAPTCHA_SITE_KEY=None, RECAPTCHA_SECRET_KEY=None, ACCOUNT_FORMS={})
    def test_without_a_recaptcha_key_mobile_sign_up_needs_none(self):
        page = Client().get('/mobile/auth/signup/')
        self.assertNotContains(page, 'recaptcha/api.js')
        response = self.sign_up('new@example.com', self.PASSWORD)
        self.assertRedirects(response, '/mobile/auth/fetch/', fetch_redirect_response=False)
        self.assertTrue(self.created('new@example.com'))

    @override_settings(RECAPTCHA_SITE_KEY='site-key', RECAPTCHA_SECRET_KEY='secret-key',
                       ACCOUNT_FORMS={'signup': 'app.forms.RecaptchaSignupForm'})
    def test_with_a_recaptcha_key_mobile_sign_up_needs_a_token(self):
        page = Client().get('/mobile/auth/signup/')
        self.assertContains(page, 'recaptcha/api.js?render=site-key')
        self.assertContains(page, 'name="recaptcha_token"')

        response = self.sign_up('bot@example.com', self.PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.created('bot@example.com'))

        answer = Response()
        answer.status_code = 200
        answer._content = b'{"success": true, "action": "signup_form"}'
        with patch('app.forms.requests.post', return_value=answer) as verify:
            response = self.sign_up('person@example.com', self.PASSWORD, recaptcha_token='token-from-google')
        self.assertEqual(verify.call_args.kwargs['data'], {'response': 'token-from-google', 'secret': 'secret-key'})
        self.assertRedirects(response, '/mobile/auth/fetch/', fetch_redirect_response=False)
        self.assertTrue(self.created('person@example.com'))

    def test_an_all_number_password_is_refused(self):
        response = self.sign_up('digits@example.com', '48213975')
        self.assertContains(response, 'This password is entirely numeric.')
        self.assertFalse(self.created('digits@example.com'))

    def test_a_password_like_the_email_address_is_refused(self):
        response = self.sign_up('jordan.whitfield@example.com', 'jordan.whitfield')
        self.assertContains(response, 'The password is too similar to the')
        self.assertFalse(self.created('jordan.whitfield@example.com'))


class PasswordChangeAndSetTestCase(TestCase):
    """The change-password and set-password pages say why a new password was refused."""

    OLD = 'violet-harbor-1847'

    def setUp(self):
        self.user = User.objects.create_user(email='keeper@example.com', password=self.OLD)
        EmailAddress.objects.create(user=self.user, email=self.user.email, primary=True, verified=True)
        self.client = Client()
        self.client.force_login(self.user)

    def test_change_password_shows_why_the_new_one_was_refused(self):
        response = self.client.post('/accounts/password/change/', {
            'oldpassword': self.OLD, 'password1': '48213975', 'password2': '48213975'})
        self.assertContains(response, 'This password is entirely numeric.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.OLD))

    def test_change_password_leaves_short_passwords_to_the_server(self):
        page = self.client.get('/accounts/password/change/')
        self.assertNotContains(page, 'pattern=')
        response = self.client.post('/accounts/password/change/', {
            'oldpassword': self.OLD, 'password1': 'k7#q', 'password2': 'k7#q'})
        self.assertContains(response, 'at least 8 characters')

    def test_set_password_shows_why_the_new_one_was_refused(self):
        self.user.set_unusable_password()
        self.user.save()
        self.client.force_login(self.user)
        page = self.client.get('/accounts/password/set/')
        self.assertNotContains(page, 'pattern=')
        response = self.client.post('/accounts/password/set/', {
            'password1': '48213975', 'password2': '48213975'})
        self.assertContains(response, 'This password is entirely numeric.')
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_usable_password())
