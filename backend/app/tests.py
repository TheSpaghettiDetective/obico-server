from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import ANY, patch, PropertyMock
from packaging.version import InvalidVersion
from requests import Response
from requests.exceptions import HTTPError

from app.models import GCodeFile, MobileDevice, Print, Printer, PrinterEvent, SharedResource, User
from app.models.syndicate_models import Syndicate
from app.views.tunnelv2_views import is_plugin_version_supported
from lib import mobile_notifications
from lib.url_signing import HmacSignedUrl, new_signed_url
from lib.utils import get_rotated_pic_url


class PrinterEventTestCase(TestCase):

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
        site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'testserver', 'name': 'testserver'})
        syndicate.sites.add(site)
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

    def test_urls_keep_their_host_and_get_valid_digest(self):
        call_command('resign_media_urls')

        self.print.refresh_from_db()
        self.assertTrue(self.print.video_url.startswith(
            'http://old-host:3334/media/tsd-timelapses/private/1.mp4?digest='))
        self.assertTrue(HmacSignedUrl(self.print.video_url).is_authorized())

        self.gcode_file.refresh_from_db()
        self.assertTrue(self.gcode_file.url.startswith('/media/g_code_files/1.gcode?digest='))
        self.assertTrue(HmacSignedUrl(self.gcode_file.url).is_authorized())


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
@override_settings(SITE_ID=1)
class PageContextTurnTestCase(TestCase):
    """TURN credentials reach clients through printer data (API/WebSocket), never page context."""

    def setUp(self):
        syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'base'})
        site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'testserver', 'name': 'testserver'})
        syndicate.sites.add(site)
        self.user = User.objects.create(email='pagecontext@test.com', syndicate=syndicate, is_pro=True)
        self.printer = Printer.objects.create(user=self.user, auth_token='pagecontexttoken')
        SharedResource.objects.create(printer=self.printer, share_token='sharetoken123')

    def syndicate_context(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.context['page_context']['syndicate']

    @override_settings(TURN_SERVER='turn.example.com', TURN_SECRET='shared', TURN_USERNAME=None, TURN_CREDENTIAL=None)
    def test_login_page_has_no_turn(self):
        self.assertNotIn('turn', self.syndicate_context('/accounts/login/'))

    @override_settings(TURN_SERVER='turn.example.com', TURN_SECRET='shared', TURN_USERNAME=None, TURN_CREDENTIAL=None)
    def test_authenticated_page_has_no_turn(self):
        self.client.force_login(self.user)
        self.assertNotIn('turn', self.syndicate_context('/printers/'))

    @override_settings(TURN_SERVER='turn.example.com', TURN_SECRET='shared', TURN_USERNAME=None, TURN_CREDENTIAL=None)
    def test_shared_page_has_no_turn(self):
        self.assertNotIn('turn', self.syndicate_context('/printers/share_token/sharetoken123/'))
