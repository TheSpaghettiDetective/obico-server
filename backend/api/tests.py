from django.test import TestCase, override_settings
from unittest.mock import *
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.urls import reverse
from safedelete.models import *
from django.contrib.sites.models import Site

from app.models import Printer, Print, User
from app.models.syndicate_models import Syndicate
from api.octoprint_views import *
from api.octoprint_messages import process_printer_status


def setup_syndicate():
    """Create a syndicate and associate it with a site for tests."""
    syndicate, _ = Syndicate.objects.get_or_create(id=1, defaults={'name': 'test'})
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'testserver', 'name': 'testserver'})
    syndicate.sites.add(site)
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