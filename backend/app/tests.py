import os
import tempfile
import uuid
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
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


class SiteSyndicateMigrationTestCase(TestCase):
    """Migration 0086, from the many-to-many link to one syndicate per site.
    PostgreSQL rolls the schema back with the test's transaction."""
    before = [('app', '0085_printerprediction_normalized_p')]
    after = [('app', '0086_sitesyndicate')]

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

        # The rows' foreign key checks are deferred to the end of the
        # transaction, and a table with checks pending cannot be dropped.
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
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
