from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from unittest.mock import *
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from safedelete.models import *
from django.contrib.sites.models import Site

from app.models import GCodeFile, GCodeFolder, OneTimeVerificationCode, Printer, Print, User, SiteSyndicate
from app.models.syndicate_models import Syndicate
from api.octoprint_views import *
from api.octoprint_messages import process_printer_status
from api.serializers import PrinterSerializer
from lib import channels


def setup_syndicate():
    """Create a syndicate and associate it with a site for tests."""
    syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'testserver', 'name': 'testserver'})
    SiteSyndicate.objects.update_or_create(site=site, defaults={'syndicate': syndicate})
    return syndicate


def init_data():
    syndicate = setup_syndicate()
    user = User.objects.create(email='test@tsd.com', syndicate=syndicate)
    user.set_password('test')
    user.save()
    printer = Printer.objects.create(user=user)
    print = Print.objects.create(
        user=user, printer=printer, filename='test.gcode', started_at=timezone.now(), ext_id=1)
    printer.current_print = print
    printer.save()
    client = Client()
    client.force_login(user)

    return (user, printer, client)


@override_settings(SITE_ID=1)
class PrinterSerializerTestCase(TestCase):
    def setUp(self):
        (_, self.printer, _) = init_data()

    @patch('lib.channels.num_ws_connections', return_value=1)
    def test_agent_connected_when_agent_websocket_is_present(self, num_ws_connections):
        data = PrinterSerializer(self.printer).data

        self.assertTrue(data['agent_connected'])
        num_ws_connections.assert_called_once_with(
            channels.octo_group_name(self.printer.id)
        )

    @patch('lib.channels.num_ws_connections', return_value=0)
    def test_agent_disconnected_when_agent_websocket_is_absent(self, num_ws_connections):
        data = PrinterSerializer(self.printer).data

        self.assertFalse(data['agent_connected'])


@override_settings(SITE_ID=1)
class GCodeFileUploadTestCase(TestCase):
    def setUp(self):
        syndicate = setup_syndicate()
        self.user = User.objects.create(email='gcode-upload@test.com', syndicate=syndicate)
        self.user.set_password('test')
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

    @patch('api.viewsets.save_file_obj')
    def test_invalid_gcode_upload_returns_400_without_creating_file(self, save_file_obj):
        upload = SimpleUploadedFile(
            'invalid.gcode',
            (
                b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x03\x00\xb7\x00\x01\x00\x00\x00not really gcode\n'
            ),
            content_type='application/octet-stream',
        )

        response = self.client.post('/api/v1/g_code_files/', {
            'filename': 'invalid.gcode',
            'file': upload,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'error': 'Invalid G-code file. Please upload a valid text G-code file.'},
        )
        self.assertFalse(
            GCodeFile.objects.all_with_deleted().filter(user=self.user, filename='invalid.gcode').exists()
        )
        save_file_obj.assert_not_called()

    @patch('api.viewsets.save_file_obj', return_value=('internal-url', 'external-url'))
    @patch(
        'api.viewsets.gcode_metadata.parse',
        return_value=({'estimated_time': 120, 'filament_total': 12.5}, []),
    )
    def test_valid_gcode_upload_still_succeeds(self, parse, save_file_obj):
        upload = SimpleUploadedFile(
            'valid.gcode',
            b'G1 X10 Y10 E0.01\n',
            content_type='application/octet-stream',
        )

        response = self.client.post('/api/v1/g_code_files/', {
            'filename': 'valid.gcode',
            'file': upload,
        })

        self.assertEqual(response.status_code, 201)
        gcode_file = GCodeFile.objects.get(user=self.user, filename='valid.gcode')
        self.assertEqual(gcode_file.num_bytes, 17)
        self.assertEqual(gcode_file.url, 'external-url')
        self.assertEqual(gcode_file.estimated_time, 120)
        self.assertEqual(gcode_file.filament_total, 12.5)
        parse.assert_called_once()
        save_file_obj.assert_called_once()


class AgentGCodeFileTestCase(SimpleTestCase):
    @patch.object(GCodeFileView, 'get_queryset')
    def test_missing_safe_filename_returns_400(self, get_queryset):
        request = APIRequestFactory().post('/api/v1/octo/g_code_files/', {
            'num_bytes': '0',
            'agent_signature': 'ts:0',
            'url': '',
        })
        force_authenticate(
            request,
            user=Mock(is_authenticated=True),
            token=Mock(id=1),
        )

        response = GCodeFileView.as_view({'post': 'post'})(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn('safe_filename', response.data)
        get_queryset.assert_not_called()


@override_settings(SITE_ID=1)
class GCodeFileListingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        syndicate = setup_syndicate()
        cls.user = User.objects.create(email='gcode-list@test.com', syndicate=syndicate)
        cls.printer = Printer.objects.create(user=cls.user, auth_token='gcode-list-test-token')
        cls.files = GCodeFile.objects.bulk_create([
            GCodeFile(
                user=cls.user,
                filename=f'file-{i}.gcode',
                safe_filename=f'file-{i}.gcode',
                metadata_json='{"estimated_time": 120, "padding": "' + 'x' * 4096 + '"}',
                agent_signature=f'ts:{i}',
                num_bytes=123,
            )
            for i in range(105)
        ])
        cls.print = Print.objects.create(
            user=cls.user, printer=cls.printer, g_code_file=cls.files[-1],
            filename=cls.files[-1].filename, started_at=timezone.now(), ext_id=1,
        )

    def agent_get(self, url):
        return self.client.get(url, HTTP_AUTHORIZATION=f'Token {self.printer.auth_token}')

    def file_select_queries(self, queries):
        return [
            query['sql'] for query in queries
            if query['sql'].startswith('SELECT')
            and 'FROM "app_gcodefile"' in query['sql']
            and 'COUNT(' not in query['sql']
        ]

    def test_agent_listing_limits_the_database_query(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.agent_get('/api/v1/octo/g_code_files/?page_size=9999')

        self.assertEqual(response.status_code, 200)
        selects = self.file_select_queries(queries)
        self.assertTrue(selects)
        self.assertIn('LIMIT 100', selects[0])
        self.assertEqual(len(response.json()['results']), 100)
        self.assertIsNotNone(response.json()['next'])

    def test_agent_default_listing_does_not_load_metadata_or_history(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.agent_get('/api/v1/octo/g_code_files/?limit=1&page=1')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['count'], 105)
        self.assertEqual(len(body['results']), 6)
        self.assertEqual(body['results'][0]['id'], self.files[0].id)
        self.assertNotIn('metadata_json', body['results'][0])
        self.assertNotIn('print_set', body['results'][0])
        selects = self.file_select_queries(queries)
        self.assertEqual(len(selects), 1)
        self.assertIn('LIMIT 6', selects[0])
        self.assertNotIn('metadata_json', selects[0])
        self.assertFalse(any('FROM "app_print"' in query['sql'] for query in queries))

    def test_agent_next_links_cover_the_library_without_duplicates(self):
        url = '/api/v1/octo/g_code_files/?page_size=24'
        ids = []
        for _ in range(5):
            self.assertIsNotNone(url)
            response = self.agent_get(url)
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertLessEqual(len(body['results']), 24)
            ids.extend(file['id'] for file in body['results'])
            url = body['next']

        self.assertIsNone(url)
        self.assertEqual(ids, [file.id for file in self.files])

    def test_mobile_listing_limits_the_database_query(self):
        self.client.force_login(self.user)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/v1/g_code_files/?page_size=9999')

        self.assertEqual(response.status_code, 200)
        selects = self.file_select_queries(queries)
        self.assertTrue(selects)
        self.assertIn('LIMIT 100', selects[0])
        self.assertEqual(len(response.json()['results']), 100)
        self.assertIsNotNone(response.json()['next'])

    def test_mobile_pages_and_details_keep_metadata_and_print_history(self):
        self.client.force_login(self.user)
        for page_size in (24, 25):
            with self.subTest(page_size=page_size):
                response = self.client.get(f'/api/v1/g_code_files/?page_size={page_size}')
                self.assertEqual(response.status_code, 200)
                body = response.json()
                self.assertEqual(set(body), {'count', 'next', 'previous', 'results'})
                self.assertEqual(body['count'], 105)
                self.assertEqual(len(body['results']), page_size)
                file = body['results'][0]
                self.assertEqual(file['metadata_json'], self.files[-1].metadata_json)
                self.assertEqual(file['print_set'][0]['id'], self.print.id)
                second_page = self.client.get(body['next']).json()['results']
                self.assertFalse({f['id'] for f in body['results']} & {f['id'] for f in second_page})

        detail = self.client.get(f'/api/v1/g_code_files/{self.files[-1].id}/').json()
        self.assertEqual(detail['metadata_json'], self.files[-1].metadata_json)
        self.assertEqual(detail['print_set'][0]['id'], self.print.id)

    def test_default_and_invalid_page_sizes_remain_bounded(self):
        self.client.force_login(self.user)
        for endpoint in ('/api/v1/g_code_files/', '/api/v1/octo/g_code_files/'):
            for query in ('', '?page_size=0', '?page_size=-1', '?page_size=invalid'):
                with self.subTest(endpoint=endpoint, query=query):
                    response = self.agent_get(endpoint + query) if '/octo/' in endpoint else self.client.get(endpoint + query)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(response.json()['results']), 6)

    def test_folder_listing_keeps_its_existing_page_size(self):
        GCodeFolder.objects.bulk_create([
            GCodeFolder(user=self.user, name=f'folder-{i}', safe_name=f'folder-{i}')
            for i in range(120)
        ])
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/g_code_folders/?parent_folder=null&page_size=9999')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 120)
        self.assertIsNone(response.json()['next'])

    def test_listings_exclude_other_accounts_and_deleted_files(self):
        other_user = User.objects.create(email='other-gcode-list@test.com', syndicate=self.user.syndicate)
        GCodeFile.objects.create(user=other_user, filename='other.gcode', safe_filename='other.gcode')
        self.files[0].delete()
        self.assertEqual(self.client.get('/api/v1/octo/g_code_files/').status_code, 401)
        agent = self.agent_get('/api/v1/octo/g_code_files/').json()
        self.assertEqual(agent['count'], 104)
        self.assertEqual(agent['results'][0]['id'], self.files[1].id)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/v1/g_code_files/').json()['count'], 104)

    def test_agent_upsert_and_patch_keep_the_existing_response(self):
        auth = {'HTTP_AUTHORIZATION': f'Token {self.printer.auth_token}'}
        data = {
            'filename': 'agent.gcode', 'safe_filename': 'agent.gcode',
            'agent_signature': 'ts:agent', 'metadata_json': '{"estimated_time": 60}',
            'num_bytes': 123, 'url': '',
        }
        response = self.client.post('/api/v1/octo/g_code_files/', data, **auth)
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body['metadata_json'], data['metadata_json'])
        self.assertEqual(body['resident_printer'], self.printer.id)
        self.assertIn('print_set', body)
        upsert = self.client.post('/api/v1/octo/g_code_files/', data, **auth)
        self.assertEqual(upsert.status_code, 200)
        self.assertEqual(upsert.json()['id'], body['id'])
        patch = self.client.patch(
            f'/api/v1/octo/g_code_files/{body["id"]}/',
            {'metadata_json': '{"estimated_time": 90}'},
            content_type='application/json', **auth,
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()['metadata_json'], '{"estimated_time": 90}')
        self.assertIn('print_set', patch.json())

    def test_agent_can_set_only_a_bare_file_name(self):
        auth = {'HTTP_AUTHORIZATION': f'Token {self.printer.auth_token}'}
        data = {
            'filename': 'cube.gcode', 'safe_filename': '../models/cube.gcode',
            'agent_signature': 'ts:cube', 'num_bytes': 123, 'url': '',
        }
        created = self.client.post('/api/v1/octo/g_code_files/', data, **auth)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()['safe_filename'], 'cube.gcode')
        file_url = f'/api/v1/octo/g_code_files/{created.json()["id"]}/'
        for sent, kept in (('..\\..\\cube2.gcode', 'cube2.gcode'), ('cube3.gcode', 'cube3.gcode')):
            with self.subTest(sent=sent):
                patch = self.client.patch(file_url, {'safe_filename': sent}, content_type='application/json', **auth)
                self.assertEqual(patch.status_code, 200)
                self.assertEqual(GCodeFile.objects.get(id=created.json()['id']).safe_filename, kept)
        for sent in ('..', 'models/..'):
            with self.subTest(sent=sent):
                patch = self.client.patch(file_url, {'safe_filename': sent}, content_type='application/json', **auth)
                self.assertEqual(patch.status_code, 400)

# https://docs.python.org/3/library/unittest.mock.html#where-to-patch for why it is patching "api.octoprint_views.send_failure_alert" not "lib.notifications.send_failure_alert"

def status_msg(print_ts, filename, event):
    return {
        "current_print_ts": print_ts,
        "octoprint_event": {"data": {"origin": "local", "name": filename}, "event_type": event, },
        "octoprint_data": {"job": {"file": {"origin": "local", "name": filename}}},
    }

def status_msg_without_event(print_ts, filename):
    return {
        "current_print_ts": print_ts,
        "octoprint_data": {"job": {"file": {"origin": "local", "name": filename}}},
    }

@override_settings(SITE_ID=1)
@patch('api.octoprint_views.send_failure_alert')
class AlertTestCase(TestCase):
    def setUp(self):
        (self.user, self.printer, self.client) = init_data()

    def test_mute_after_the_print_ended_mutes_nothing(self, send_failure_alert):
        # The alert stays on a page that is still open; the person taps mute
        # after the print was cancelled (OBICO-SERVER-B2K).
        self.printer.current_print = None
        self.printer.save()

        response = self.client.post(
            '/api/v1/printers/{}/mute_current_print/?mute_alert=true'.format(self.printer.id))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['succeeded'])
        self.assertIsNone(response.json()['printer']['current_print'])

    def test_warning_once_and_cancel(self, send_failure_alert):
        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=True, print_paused=False)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)

        response = self.client.get(
            '/api/v1/printers/{}/cancel_print/'.format(self.printer.id))
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at >
                        self.printer.current_print.alerted_at)
        self.assertEqual(
            self.printer.current_print.alert_overwrite, Print.FAILED)

    def test_warning_once_and_acknowledge(self, send_failure_alert):
        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=True, print_paused=False)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)

        response = self.client.get(
            '/api/v1/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at >
                        self.printer.current_print.alerted_at)
        self.assertEqual(
            self.printer.current_print.alert_overwrite, Print.NOT_FAILED)

    def test_warning_twice(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer, None)

        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=True, print_paused=False)

    def test_error_twice(self, send_failure_alert):
        pause_if_needed(self.printer, None)
        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)

    def test_warning_twice_acknowledged_in_between(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer, None)
            self.client.get(
                '/api/v1/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        alert_if_needed(self.printer, None)
        self.assertEqual(send_failure_alert.call_count, 2)

    def test_warning_twice_acknowledged_muted_in_between(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer, None)
        with patch('django.utils.timezone.now', return_value=(timezone.now() - timedelta(minutes=30))):
            self.client.get(
                '/api/v1/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))
            self.client.get(
                '/api/v1/printers/{}/mute_current_print/'.format(self.printer.id), {'mute_alert': 'true'})

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at >
                        self.printer.current_print.alerted_at)
        self.assertEqual(
            self.printer.current_print.alert_overwrite, Print.NOT_FAILED)

        alert_if_needed(self.printer, None)
        self.assertEqual(send_failure_alert.call_count, 1)

    def test_warning_not_alerted_again_shortly_after_acknowledged(self, send_failure_alert):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        with patch('django.utils.timezone.now', return_value=one_minute_ago):
            alert_if_needed(self.printer, None)
            self.client.get(
                '/api/v1/printers/{}/resume_print/'.format(self.printer.id))

        self.printer.refresh_from_db()
        alert_if_needed(self.printer, None)
        self.assertEqual(send_failure_alert.call_count, 1)

    def test_error_once_and_acknowledge(self, send_failure_alert):
        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

        self.client.get(
            '/api/v1/printers/{}/cancel_print/'.format(self.printer.id))
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at >
                        self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_then_error(self, send_failure_alert):
        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_with(
            self.printer, None, is_warning=True, print_paused=False)
        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_with(
            self.printer, None, is_warning=False, print_paused=True)
        self.assertEqual(send_failure_alert.call_count, 2)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_error_then_warning(self, send_failure_alert):
        pause_if_needed(self.printer, None)
        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_acknowledged_then_error(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer, None)
            send_failure_alert.assert_called_with(
                self.printer, None, is_warning=True, print_paused=False)
            self.client.get(
                '/api/v1/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_with(
            self.printer, None, is_warning=False, print_paused=True)
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_acknowledged_then_error_shortly_after(self, send_failure_alert):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        with patch('django.utils.timezone.now', return_value=one_minute_ago):
            alert_if_needed(self.printer, None)
            self.client.get(
                '/api/v1/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer, None)
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=True, print_paused=False)

    def test_error_resumed_then_warning(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer, None)
            send_failure_alert.assert_called_with(
                self.printer, None, is_warning=False, print_paused=True)
        with patch('django.utils.timezone.now', return_value=(timezone.now() - timedelta(minutes=30))):
            self.client.get(
                '/api/v1/printers/{}/resume_print/'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at >
                        self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_with(
            self.printer, None, is_warning=True, print_paused=False)
        self.assertEqual(send_failure_alert.call_count, 2)
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at <
                        self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_error_resumed_then_warning_error_shortly_after(self, send_failure_alert):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        with patch('django.utils.timezone.now', return_value=one_minute_ago):
            pause_if_needed(self.printer, None)
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintResumed'))

        alert_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)
        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)

    def test_error_resumed_muted_then_error(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer, None)
        with patch('django.utils.timezone.now', return_value=timezone.now() - timedelta(hours=0.5)):
            self.client.get(
                '/api/v1/printers/{}/resume_print/'.format(self.printer.id))
            self.client.get(
                '/api/v1/printers/{}/mute_current_print/'.format(self.printer.id), {'mute_alert': 'true'})

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer, None)
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)

        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=True)

    def test_error_not_paused_if_configured_so(self, send_failure_alert):
        self.printer.action_on_failure = Printer.NONE
        self.printer.save()
        pause_if_needed(self.printer, None)
        send_failure_alert.assert_called_once_with(
            self.printer, None, is_warning=False, print_paused=False)

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNone(self.printer.current_print.paused_at)


@override_settings(SITE_ID=1)
@patch.object(Printer, 'pause_print')
class PauseTestCase(TestCase):
    def setUp(self):
        (self.user, self.printer, self.client) = init_data()

    def test_pause_resumed_in_octoprint_not_paused_again(self, pause_print):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer, None)
            process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintResumed'))

        pause_if_needed(self.printer, None)
        pause_print.assert_called_once()


@override_settings(PRINT_EVENT_HANDLER='app.tasks.process_print_events', SITE_ID=1)
@patch('app.models.celery_app')
class OAuthPrinterFlowTestCase(TestCase):
    """Test the start_print and finish_print API actions for OAuth apps."""

    def setUp(self):
        syndicate = setup_syndicate()
        self.user = User.objects.create(email='oauth@test.com', syndicate=syndicate)
        self.user.set_password('test')
        self.user.save()
        self.printer = Printer.objects.create(user=self.user, name='OAuth Test Printer')
        self.client = Client()
        self.client.force_login(self.user)

    def test_start_print_success(self, celery_app):
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {'filename': 'test_oauth.gcode'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print)
        self.assertEqual(self.printer.current_print.filename, 'test_oauth.gcode')

    def test_start_print_requires_filename(self, celery_app):
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_start_print_auto_closes_existing_print(self, celery_app):
        # Start first print
        self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {'filename': 'first.gcode'},
            content_type='application/json'
        )
        self.printer.refresh_from_db()
        first_print_id = self.printer.current_print.id

        # Start second print - should auto-close first
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {'filename': 'second.gcode'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.printer.refresh_from_db()

        # Verify new print is active
        self.assertEqual(self.printer.current_print.filename, 'second.gcode')

        # Verify old print was finished
        old_print = Print.objects.get(id=first_print_id)
        self.assertIsNotNone(old_print.finished_at)

    def test_finish_print_success(self, celery_app):
        # Start a print first
        self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {'filename': 'test.gcode'},
            content_type='application/json'
        )
        self.printer.refresh_from_db()
        print_id = self.printer.current_print.id

        # Finish the print
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/finish_print/',
            {'status': 'success'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print)

        # Check print is marked as finished
        print_obj = Print.objects.get(id=print_id)
        self.assertIsNotNone(print_obj.finished_at)
        self.assertIsNone(print_obj.cancelled_at)

    def test_finish_print_cancelled(self, celery_app):
        # Start a print first
        self.client.post(
            f'/api/v1/printers/{self.printer.id}/start_print/',
            {'filename': 'test.gcode'},
            content_type='application/json'
        )
        self.printer.refresh_from_db()
        print_id = self.printer.current_print.id

        # Cancel the print
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/finish_print/',
            {'status': 'cancelled'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Check print is marked as cancelled
        print_obj = Print.objects.get(id=print_id)
        self.assertIsNotNone(print_obj.cancelled_at)

    def test_finish_print_fails_if_not_printing(self, celery_app):
        response = self.client.post(
            f'/api/v1/printers/{self.printer.id}/finish_print/',
            {},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_create_printer(self, celery_app):
        """Test creating a new printer via API."""
        response = self.client.post(
            '/api/v1/printers/',
            {'name': 'New OAuth Printer'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'New OAuth Printer')
        self.assertIsNotNone(data.get('auth_token'))
        # Verify printer was created in database for this user
        self.assertTrue(Printer.objects.filter(id=data['id'], user=self.user).exists())


def make_jpeg(size=(64, 48)):
    import io, random
    from PIL import Image as PILImage
    rng = random.Random(1)
    img = PILImage.new('RGB', size)
    img.putdata([(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255)) for _ in range(size[0] * size[1])])
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=60)
    return buf.getvalue()


class CapImageSizeTestCase(SimpleTestCase):
    def upload(self, data):
        return SimpleUploadedFile('pic', data, content_type='image/jpeg')

    def test_complete_jpeg_is_accepted_unchanged(self):
        data = make_jpeg()

        pic = cap_image_size(self.upload(data))

        self.assertEqual(pic.file.read(), data)

    def test_complete_jpeg_with_trailing_zero_padding_is_accepted(self):
        cap_image_size(self.upload(make_jpeg() + b'\x00\x00\x00'))

    def test_truncated_jpeg_is_rejected(self):
        data = make_jpeg()

        for cut in (0.9, 0.5, 0.1):
            with self.subTest(kept=cut):
                with self.assertRaises(ValidationError):
                    cap_image_size(self.upload(data[:int(len(data) * cut)]))

    def test_truncated_large_jpeg_is_rejected_instead_of_being_repaired(self):
        data = make_jpeg(size=(1400, 100))

        with self.assertRaises(ValidationError):
            cap_image_size(self.upload(data[:len(data) // 2]))

    def test_jpeg_with_end_marker_but_no_scan_data_is_rejected(self):
        data = make_jpeg()
        headers_only = data[:data.index(b'\xff\xda')] + b'\xff\xd9'

        with self.assertRaises(ValidationError):
            cap_image_size(self.upload(headers_only))


@override_settings(SITE_ID=1)
class ParentFolderFilterTestCase(TestCase):
    def setUp(self):
        syndicate = setup_syndicate()
        self.user = User.objects.create(email='parent-folder@test.com', syndicate=syndicate)
        self.client = Client()
        self.client.force_login(self.user)
        self.folder = GCodeFolder.objects.create(user=self.user, name='folder')
        GCodeFile.objects.create(
            user=self.user, filename='in.gcode', safe_filename='in.gcode', parent_folder=self.folder)

    def test_non_numeric_parent_folder_returns_400(self):
        for url in ('/api/v1/g_code_folders/', '/api/v1/g_code_files/'):
            with self.subTest(url=url):
                response = self.client.get(url, {'parent_folder': 'ToPrint'})

                self.assertEqual(response.status_code, 400)
                self.assertIn('parent_folder', response.json())

    def test_numeric_and_root_parent_folder_still_work(self):
        response = self.client.get('/api/v1/g_code_files/', {'parent_folder': self.folder.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

        for root in ('null', ''):
            response = self.client.get('/api/v1/g_code_files/', {'parent_folder': root})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()['results']), 0)


class ScrubSurrogatesTestCase(SimpleTestCase):

    def test_replaces_escaped_lone_surrogates_so_message_can_be_packed(self):
        import json, msgpack
        from api.consumers import scrub_surrogates

        # A client that json-dumps a filename holding an undecodable byte sends "\udce4" in the text frame.
        data = json.loads(json.dumps({
            'current_print_ts': 1,
            'status': {'job': {'file': {'name': 'abcdefgh\udce4.gcode'}}, 'names': ['\udcf1']},
        }))
        with self.assertRaises(UnicodeEncodeError):
            msgpack.packb(data)

        scrubbed = scrub_surrogates(data)

        self.assertEqual(scrubbed['status']['job']['file']['name'], 'abcdefgh�.gcode')
        self.assertEqual(scrubbed['status']['names'], ['�'])
        self.assertEqual(scrubbed['current_print_ts'], 1)
        msgpack.packb(scrubbed)

    def test_leaves_valid_text_untouched(self):
        import json
        from api.consumers import scrub_surrogates

        # An escaped surrogate pair is decoded by json.loads into a real emoji and must survive.
        data = json.loads('{"name": "caf\\u00e9 \\ud83d\\ude00", "n": null, "ok": true}')
        self.assertEqual(scrub_surrogates(data), {'name': 'café 😀', 'n': None, 'ok': True})


@override_settings(SITE_ID=1)
@patch('lib.channels.send_msg_to_printer')
@patch('api.viewsets.send_status_to_web')
class PrinterOwnershipTestCase(TestCase):
    """A user must not be able to read or take over another user's printer."""

    def setUp(self):
        (self.user, self.printer, self.client) = init_data()
        self.printer.auth_token = 'own-token'
        self.printer.save()
        self.other_user = User.objects.create(email='other@tsd.com', syndicate=self.user.syndicate)
        self.other_printer = Printer.objects.create(user=self.other_user, name='Other Printer', auth_token='other-token')
        self.other_print = Print.objects.create(
            user=self.other_user, printer=self.other_printer, filename='other.gcode', started_at=timezone.now(), ext_id=2)

    def test_verification_code_for_another_users_printer_is_404(self, *_):
        response = self.client.get('/api/v1/onetimeverificationcodes/', {'printer_id': self.other_printer.id})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn('other-token', response.content.decode())
        self.assertFalse(OneTimeVerificationCode.objects.filter(printer=self.other_printer).exists())

    def test_verification_code_for_own_printer_still_works(self, *_):
        response = self.client.get('/api/v1/onetimeverificationcodes/', {'printer_id': self.printer.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['printer']['id'], self.printer.id)

    def test_patch_ignores_fields_the_serializer_does_not_allow(self, *_):
        own_print = self.printer.current_print
        response = self.client.patch(
            f'/api/v1/printers/{self.printer.id}/',
            {'name': 'Renamed', 'current_print': self.other_print.id, 'user': self.other_user.id, 'auth_token': 'chosen'},
            content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('other-token', response.content.decode())
        self.printer.refresh_from_db()
        self.assertEqual(self.printer.name, 'Renamed')
        self.assertEqual(self.printer.current_print, own_print)
        self.assertEqual(self.printer.user, self.user)
        self.assertNotEqual(self.printer.auth_token, 'chosen')

    def test_patch_saves_settings_the_web_app_sends(self, *_):
        response = self.client.patch(
            f'/api/v1/printers/{self.printer.id}/',
            {'watching_enabled': False, 'action_on_failure': 'NONE', 'detective_sensitivity': 1.2,
             'tools_off_on_pause': False, 'min_timelapse_secs_on_finish': 60},
            content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.printer.refresh_from_db()
        self.assertFalse(self.printer.watching_enabled)
        self.assertEqual(self.printer.action_on_failure, 'NONE')
        self.assertEqual(self.printer.detective_sensitivity, 1.2)
        self.assertFalse(self.printer.tools_off_on_pause)
        self.assertEqual(self.printer.min_timelapse_secs_on_finish, 60)

    def test_patch_rejects_invalid_value(self, *_):
        response = self.client.patch(
            f'/api/v1/printers/{self.printer.id}/', {'action_on_failure': 'BOGUS'}, content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_patch_another_users_printer_is_404(self, *_):
        response = self.client.patch(
            f'/api/v1/printers/{self.other_printer.id}/', {'name': 'Mine now'}, content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.other_printer.refresh_from_db()
        self.assertEqual(self.other_printer.name, 'Other Printer')

    def test_agent_patch_only_renames(self, *_):
        own_print = self.printer.current_print
        response = Client().patch(
            '/api/v1/octo/printer/',
            {'name': 'Renamed by agent', 'current_print': self.other_print.id, 'user': self.other_user.id},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.printer.auth_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['printer']['name'], 'Renamed by agent')
        self.printer.refresh_from_db()
        self.assertEqual(self.printer.name, 'Renamed by agent')
        self.assertEqual(self.printer.current_print, own_print)
        self.assertEqual(self.printer.user, self.user)

    def test_printer_nested_in_a_print_has_no_auth_token(self, *_):
        data = PrinterSerializer(self.printer).data

        self.assertIn('auth_token', data)
        self.assertNotIn('auth_token', data['current_print']['printer'])



@override_settings(SITE_ID=1)
class GCodeFileAddressTestCase(TestCase):
    """The file and thumbnail addresses of a G-code file are written by the server only."""

    ADDRESS_FIELDS = ('url', 'thumbnail1_url', 'thumbnail2_url', 'thumbnail3_url')

    def setUp(self):
        (self.user, self.printer, self.client) = init_data()
        self.printer.auth_token = 'gcode-address-test-token'
        self.printer.save()
        self.stored = GCodeFile.objects.create(
            user=self.user, filename='a.gcode', safe_filename='a.gcode',
            url='/media/tsd-gcodes/1/1?digest=x', thumbnail1_url='/media/tsd-timelapses/1.png?digest=x')
        self.planted = {field: 'http://anything.example/media//etc/passwd' for field in self.ADDRESS_FIELDS}

    def test_web_create_ignores_addresses(self):
        response = self.client.post('/api/v1/g_code_files/', {'filename': 'p.gcode', **self.planted},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        created = GCodeFile.objects.get(id=response.json()['id'])
        for field in self.ADDRESS_FIELDS:
            self.assertIsNone(getattr(created, field))

    def test_web_update_ignores_addresses(self):
        response = self.client.patch(f'/api/v1/g_code_files/{self.stored.id}/', {'filename': 'b.gcode', **self.planted},
                                     content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.stored.refresh_from_db()
        self.assertEqual(self.stored.filename, 'b.gcode')
        self.assertEqual(self.stored.url, '/media/tsd-gcodes/1/1?digest=x')
        self.assertEqual(self.stored.thumbnail1_url, '/media/tsd-timelapses/1.png?digest=x')
        self.assertIsNone(self.stored.thumbnail2_url)

    def test_agent_update_ignores_addresses_but_records_where_it_stored_the_file(self):
        # What OctoPrint-Obico and moonraker-obico send after downloading a file to print
        response = self.client.patch(
            f'/api/v1/octo/g_code_files/{self.stored.id}/',
            {'agent_signature': 'md5:abc', 'safe_filename': 'a_1.gcode', **self.planted},
            content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.printer.auth_token}')

        self.assertEqual(response.status_code, 200)
        self.stored.refresh_from_db()
        self.assertEqual(self.stored.agent_signature, 'md5:abc')
        self.assertEqual(self.stored.safe_filename, 'a_1.gcode')
        self.assertEqual(self.stored.url, '/media/tsd-gcodes/1/1?digest=x')
        self.assertEqual(self.stored.thumbnail1_url, '/media/tsd-timelapses/1.png?digest=x')
        self.assertIsNone(self.stored.thumbnail2_url)


LOCAL_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(SITE_ID=1, CACHES=LOCAL_CACHE)
class LinkCodeGuessingTestCase(TestCase):
    """Wrong 6-digit codes and wrong one-time passcodes are limited per client
    and per account, not per guessed value."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        (self.user, self.printer, self.client) = init_data()

    def verify(self, code, ip='198.51.100.7'):
        return Client(REMOTE_ADDR=ip).get(f'/api/v1/octo/verify/?code={code}')

    def test_verify_answers_instead_of_crashing(self):
        self.assertEqual(self.verify('123456').status_code, 404)

    def test_a_client_trying_different_codes_is_stopped(self):
        OneTimeVerificationCode.objects.create(user=self.user, code='424242')
        for n in range(VERIFY_CODE_MAX_FAILURES_PER_CLIENT):
            self.assertEqual(self.verify(f'{100000 + n}').status_code, 404)
        self.assertEqual(self.verify('424242').status_code, 429)
        self.assertEqual(self.verify('424242', ip='198.51.100.8').status_code, 200)

    def test_a_success_does_not_clear_the_failures(self):
        OneTimeVerificationCode.objects.create(user=self.user, code='111111')
        for n in range(VERIFY_CODE_MAX_FAILURES_PER_CLIENT - 1):
            self.verify(f'{100000 + n}')
        self.assertEqual(self.verify('111111').status_code, 200)
        self.verify('100099')
        OneTimeVerificationCode.objects.create(user=self.user, code='222222')
        self.assertEqual(self.verify('222222').status_code, 429)

    def test_guessing_a_code_before_it_is_issued_does_not_block_its_owner(self):
        for _ in range(5):
            self.verify('515151')
        OneTimeVerificationCode.objects.create(user=self.user, code='515151')
        self.assertEqual(self.verify('515151', ip='198.51.100.8').status_code, 200)

    @patch('api.viewsets.check_one_time_passcode', return_value=False)
    def test_an_account_trying_different_passcodes_is_stopped(self, check):
        from api.viewsets import ONE_TIME_PASSCODE_MAX_FAILURES_PER_USER
        OneTimeVerificationCode.objects.create(user=self.user, code='626262')

        def submit(passcode):
            return self.client.post('/api/v1/one_time_passcodes/', {'verification_code': '626262', 'one_time_passcode': passcode},
                                    content_type='application/json').status_code

        for n in range(ONE_TIME_PASSCODE_MAX_FAILURES_PER_USER):
            self.assertEqual(submit(f'zz{n:03d}'), 404)
        check.return_value = True
        self.assertEqual(submit('right'), 429)
        self.assertEqual(check.call_count, ONE_TIME_PASSCODE_MAX_FAILURES_PER_USER)


class LinkCodeGenerationTestCase(SimpleTestCase):

    @patch('lib.one_time_passcode.set_value_by_one_time_passcode')
    @patch('lib.one_time_passcode.lookup_value_by_one_time_passcode', return_value=None)
    @patch('lib.one_time_passcode.secrets.choice', return_value='7')
    def test_passcodes_come_from_secrets_in_the_same_format(self, choice, *_):
        from lib.one_time_passcode import request_one_time_passcode
        self.assertEqual(request_one_time_passcode('')[0], '77777')
        self.assertEqual(set(choice.call_args.args[0]), set('abcdefghijklmnopqrstuvwxyz0123456789'))


@override_settings(SITE_ID=1, CACHES=LOCAL_CACHE)
class PrinterDiscoverySecretTestCase(TestCase):
    # Everyone here shares one address, as people behind one home or office router do
    IP = '198.51.100.77'
    DEVICE_ID = 'd' * 32
    SECRET = 's' * 64

    def setUp(self):
        self.clear_discovery_keys()
        self.user = User.objects.create(email='discovery@example.com')
        self.browser = Client(REMOTE_ADDR=self.IP)
        self.browser.force_login(self.user)

    def tearDown(self):
        self.clear_discovery_keys()

    def clear_discovery_keys(self):
        from lib.cache import REDIS
        for key in REDIS.scan_iter(f'printer_discovery:{self.IP}:*'):
            REDIS.delete(key)

    def poll(self, **extra):
        device = {'device_id': self.DEVICE_ID, 'host_or_ip': '192.168.1.50', 'port': 80, 'hostname': 'printer', **extra}
        return Client(REMOTE_ADDR=self.IP).post('/api/v1/octo/unlinked/', device, content_type='application/json')

    def link(self, secret):
        return self.browser.post('/api/v1/printer_discovery/', {'code': '424242', 'device_id': self.DEVICE_ID, 'device_secret': secret},
                                 content_type='application/json')

    def secret_hash(self, secret):
        import hashlib
        return hashlib.sha256(secret.encode()).hexdigest()

    def test_the_code_reaches_only_polls_with_the_device_secret_hash(self):
        self.assertEqual(self.poll(device_secret_hash=self.secret_hash(self.SECRET)).status_code, 200)
        self.assertEqual(self.link(self.SECRET).status_code, 200)

        self.assertEqual(self.poll().status_code, 400)
        self.assertEqual(self.poll(device_secret_hash=self.secret_hash('another secret')).status_code, 400)

        messages = self.poll(device_secret_hash=self.secret_hash(self.SECRET)).json()['messages']
        self.assertEqual([m['data']['code'] for m in messages], ['424242'])

    def test_the_hash_is_not_listed(self):
        self.poll(device_secret_hash=self.secret_hash(self.SECRET))
        listed = self.browser.get('/api/v1/printer_discovery/').json()
        self.assertEqual([d['device_id'] for d in listed], [self.DEVICE_ID])
        self.assertNotIn('device_secret_hash', listed[0])

    def test_a_secret_that_is_not_the_device_secret_is_refused(self):
        self.poll(device_secret_hash=self.secret_hash(self.SECRET))
        self.assertEqual(self.link('not the device secret').status_code, 400)
        self.assertEqual(self.poll(device_secret_hash=self.secret_hash(self.SECRET)).json()['messages'], [])

    def test_a_device_that_sends_no_hash_works_as_before(self):
        # Plugins released before the hash was added. A later poll with a hash does not take the device over.
        self.assertEqual(self.poll().status_code, 200)
        self.assertEqual(self.poll(device_secret_hash=self.secret_hash('attacker')).status_code, 200)
        self.assertEqual(self.link(self.SECRET).status_code, 200)
        messages = self.poll().json()['messages']
        self.assertEqual([m['data'] for m in messages], [{'code': '424242', 'secret': self.SECRET}])
