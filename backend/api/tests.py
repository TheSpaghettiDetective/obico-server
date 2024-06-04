from django.test import TestCase, override_settings
from unittest.mock import *
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.urls import reverse
from safedelete.models import *

from app.models import Printer, Print, User
from api.octoprint_views import *
from api.octoprint_messages import process_printer_status


def init_data():
    user = User.objects.create(email='test@tsd.com')
    user.set_password('test')
    user.save()
    printer = Printer.objects.create(user=user)
    print = Print.objects.create(
        user=user, printer=printer, filename='test.gcode', started_at=timezone.now(), ext_id=1)
    printer.current_print = print
    printer.save()
    client = Client()
    client.login(email='test@tsd.com', password='test')

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


EVENT_CALLS = [call('app.tasks.process_print_events', args=ANY)]


@override_settings(PRINT_EVENT_HANDLER='app.tasks.process_print_events')
@patch('app.models.celery_app')
class PrintTestCase(TestCase):

    def setUp(self):
        (self.user, self.printer, self.client) = init_data()
        self.printer.current_print = None
        self.printer.save()
        Print.objects.all().delete(force_policy=HARD_DELETE)

    def test_neg_print_ts_is_ignored_when_no_current_print(self, celery_app):
        process_printer_status(self.printer, status_msg(-1, '1.gcode', 'PrintStarted'))
        self.assertIsNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg(-1, '1.gcode', 'PrintFailed'))
        self.assertIsNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg(-1, '1.gcode', 'PrintCancelled'))
        self.assertIsNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg(-1, '1.gcode', 'PrintPaused'))
        self.assertIsNone(self.printer.current_print)
        celery_app.send_task.assert_not_called()

    def test_print_is_done_normally(self, celery_app):
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))
        self.assertIsNotNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintDone'))
        self.assertIsNone(self.printer.current_print)
        self.assertIsNotNone(Print.objects.first().finished_at)
        celery_app.send_task.assert_has_calls(EVENT_CALLS)
        self.assertEqual(celery_app.send_task.call_count, 1)

    def test_print_is_canceled_normally(self, celery_app):
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))
        self.assertIsNotNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintCancelled'))
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintFailed'))
        self.assertIsNone(self.printer.current_print)
        self.assertIsNone(Print.objects.first().finished_at)
        self.assertIsNotNone(Print.objects.first().cancelled_at)
        celery_app.send_task.assert_has_calls(EVENT_CALLS)
        self.assertEqual(celery_app.send_task.call_count, 1)

    def test_lost_end_event(self, celery_app):
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))
        self.assertIsNotNone(self.printer.current_print)

        process_printer_status(self.printer, status_msg_without_event(-1, '1.gcode'))
        process_printer_status(self.printer, status_msg(100, '1.gcode', 'PrintPaused'))
        self.assertIsNotNone(self.printer.current_print)
        self.assertEqual(self.printer.current_print.ext_id, 100)
        self.assertIsNotNone(self.printer.current_print.started_at)
        self.assertEqual(Print.objects.all_with_deleted().count(), 2)
        celery_app.send_task.assert_has_calls(EVENT_CALLS)
        self.assertEqual(celery_app.send_task.call_count, 1)

        process_printer_status(self.printer, status_msg(100, '1.gcode', 'PrintDone'))
        self.assertEqual(celery_app.send_task.call_count, 2)

    def test_plugin_send_neg_print_ts_while_printing(self, celery_app):
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))
        process_printer_status(self.printer, status_msg(-1, '1.gcode', 'PrintPaused'))
        self.assertIsNotNone(self.printer.current_print)
        process_printer_status(self.printer, status_msg_without_event(1, '1.gcode'))
        self.assertIsNotNone(self.printer.current_print)
        self.assertEqual(Print.objects.all_with_deleted().count(), 1)
        self.assertEqual(celery_app.send_task.call_count, 0)

    def test_race_condition_at_end_of_print(self, celery_app):
        eleven_hour_ago = timezone.now() - timedelta(hours=11)
        with patch('django.utils.timezone.now', return_value=eleven_hour_ago):
            process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))

        process_printer_status(self.printer, status_msg_without_event(-1, '1.gcode'))
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintFailed'))
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintCancelled'))
        self.assertIsNone(self.printer.current_print)
        celery_app.send_task.assert_has_calls(EVENT_CALLS)
        self.assertEqual(celery_app.send_task.call_count, 1)

    def test_plugin_send_diff_print_ts_while_printing(self, celery_app):
        process_printer_status(self.printer, status_msg(1, '1.gcode', 'PrintStarted'))
        process_printer_status(self.printer, status_msg(50, '1.gcode', 'PrintPaused'))
        process_printer_status(self.printer, status_msg_without_event(1, '1.gcode'))
        self.assertIsNotNone(self.printer.current_print)
        self.assertEqual(Print.objects.all_with_deleted().count(), 1)
        self.assertEqual(celery_app.send_task.call_count, 0)

        process_printer_status(self.printer, status_msg_without_event(100, '1.gcode'))
        celery_app.send_task.assert_has_calls(EVENT_CALLS)
        self.assertEqual(celery_app.send_task.call_count, 1)