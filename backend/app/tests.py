from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, PropertyMock

from app.models import Print, Printer, PrinterEvent, User
from app.models.syndicate_models import Syndicate
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

    def test_ended_event_preserves_printer_pic_before_task_handler(self):
        raw_path = f'raw/{self.printer.id}/{self.print.id}/123.jpg'
        raw_url = f'https://app.obico.io/ent/object_store/?t=1/tsd-pics/{raw_path}&d=x'

        with patch('app.models.other_models.cache.printer_pic_get', return_value=raw_url), \
                patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url'), \
                patch('app.models.other_models.copy_pic', return_value='cached-image-url', create=True) as copy_pic, \
                patch('app.models.other_models.cache.printer_pic_set') as printer_pic_set, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED, task_handler=True)

        copy_pic.assert_called_once_with(
            raw_path,
            f'snapshots/{self.printer.id}/latest_unrotated.jpg',
            self.user.syndicate.name,
            rotated=False,
            to_long_term_storage=False,
        )
        printer_pic_set.assert_called_once_with(
            self.printer.id,
            {'img_url': 'cached-image-url'},
            ex=60 * 30,
        )

    def test_started_event_does_not_preserve_printer_pic(self):
        with patch('app.models.other_models.cache.printer_pic_get') as printer_pic_get, \
                patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url'), \
                patch('app.models.other_models.copy_pic') as copy_pic, \
                patch('app.models.other_models.cache.printer_pic_set') as printer_pic_set, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.STARTED, task_handler=True)

        printer_pic_get.assert_not_called()
        copy_pic.assert_not_called()
        printer_pic_set.assert_not_called()

    def test_ended_event_does_not_preserve_pic_from_different_print(self):
        other_print_id = self.print.id + 1
        raw_url = (
            'https://app.obico.io/ent/object_store/'
            f'?t=1/tsd-pics/raw/{self.printer.id}/{other_print_id}/123.jpg&d=x'
        )

        with patch('app.models.other_models.cache.printer_pic_get', return_value=raw_url), \
                patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url'), \
                patch('app.models.other_models.copy_pic') as copy_pic, \
                patch('app.models.other_models.cache.printer_pic_set') as printer_pic_set, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED, task_handler=True)

        copy_pic.assert_not_called()
        printer_pic_set.assert_not_called()

    def test_ended_event_does_not_preserve_when_printer_pic_missing(self):
        with patch('app.models.other_models.cache.printer_pic_get', return_value=None), \
                patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url'), \
                patch('app.models.other_models.copy_pic') as copy_pic, \
                patch('app.models.other_models.cache.printer_pic_set') as printer_pic_set, \
                patch('app.models.other_models.celery_app'):
            PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED, task_handler=True)

        copy_pic.assert_not_called()
        printer_pic_set.assert_not_called()

    def test_ended_event_preserve_failure_bubbles_up(self):
        raw_path = f'raw/{self.printer.id}/{self.print.id}/123.jpg'
        raw_url = f'https://app.obico.io/ent/object_store/?t=1/tsd-pics/{raw_path}&d=x'

        with patch('app.models.other_models.cache.printer_pic_get', return_value=raw_url), \
                patch('app.models.other_models.copy_pic', side_effect=Exception('copy failed')), \
                patch('app.models.other_models.cache.printer_pic_set'), \
                patch('app.models.other_models.celery_app'):
            with self.assertRaisesRegex(Exception, 'copy failed'):
                PrinterEvent.create(print=self.print, event_type=PrinterEvent.ENDED, task_handler=True)

    def test_stale_current_print_updates_pic_before_starting_next_print(self):
        raw_path = f'raw/{self.printer.id}/{self.print.id}/123.jpg'
        cache_pic = {
            'img_url': f'https://app.obico.io/ent/object_store/?t=1/tsd-pics/{raw_path}&d=x',
        }
        seen_event_pic_urls = []

        def printer_pic_get(printer_id, key=None):
            return cache_pic.get(key) if key else cache_pic.copy()

        def printer_pic_set(printer_id, mapping, ex=None):
            cache_pic.update(mapping)

        def get_rotated_pic_url(printer, force_snapshot=False):
            seen_event_pic_urls.append(printer.pic['img_url'])
            return f'event-image-url-{len(seen_event_pic_urls)}'

        self.printer.current_print = self.print
        self.printer.save()

        with patch('app.models.other_models.cache.printer_pic_get', side_effect=printer_pic_get), \
                patch('app.models.other_models.cache.printer_pic_set', side_effect=printer_pic_set), \
                patch('app.models.other_models.copy_pic', return_value='cached-image-url'), \
                patch('app.models.other_models.get_rotated_pic_url', side_effect=get_rotated_pic_url), \
                patch('app.models.other_models.celery_app'):
            self.printer.update_current_print(2, None, 'new.gcode')

        self.assertEqual(seen_event_pic_urls, ['cached-image-url', 'cached-image-url'])

    def test_new_print_start_drops_stale_cached_raw_pic(self):
        raw_path = f'raw/{self.printer.id}/{self.print.id}/123.jpg'
        cache_pic = {
            'img_url': f'https://app.obico.io/ent/object_store/?t=1/tsd-pics/{raw_path}&d=x',
        }

        def printer_pic_get(printer_id, key=None):
            return cache_pic.get(key) if key else cache_pic.copy()

        def printer_pic_delete(printer_id):
            cache_pic.clear()

        def get_rotated_pic_url(printer, force_snapshot=False):
            if printer.pic and printer.pic.get('img_url'):
                raise Exception('stale cached pic used')
            return None

        with patch('app.models.other_models.cache.printer_pic_get', side_effect=printer_pic_get), \
                patch('app.models.other_models.cache.printer_pic_delete', side_effect=printer_pic_delete) as printer_pic_delete, \
                patch('app.models.other_models.get_rotated_pic_url', side_effect=get_rotated_pic_url), \
                patch('app.models.other_models.celery_app'):
            self.printer.set_current_print('new.gcode', None, 2)

        printer_pic_delete.assert_called_once_with(self.printer.id)
        self.assertEqual(cache_pic, {})
        self.assertTrue(PrinterEvent.objects.filter(print=self.printer.current_print, event_type=PrinterEvent.STARTED).exists())

    def test_new_print_start_keeps_matching_cached_raw_pic(self):
        cur_print = Print.objects.create(
            user=self.user,
            printer=self.printer,
            filename='new.gcode',
            ext_id=2,
            started_at=timezone.now(),
        )
        raw_path = f'raw/{self.printer.id}/{cur_print.id}/123.jpg'
        cache_pic = {
            'img_url': f'https://app.obico.io/ent/object_store/?t=1/tsd-pics/{raw_path}&d=x',
        }

        def printer_pic_get(printer_id, key=None):
            return cache_pic.get(key) if key else cache_pic.copy()

        with patch('app.models.other_models.cache.printer_pic_get', side_effect=printer_pic_get), \
                patch('app.models.other_models.cache.printer_pic_delete') as printer_pic_delete, \
                patch('app.models.other_models.get_rotated_pic_url', return_value='event-image-url'), \
                patch('app.models.other_models.celery_app'):
            self.printer.set_current_print('new.gcode', None, 2)

        printer_pic_delete.assert_not_called()

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
