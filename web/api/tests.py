from django.test import TestCase
from unittest.mock import *
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.urls import reverse

from app.models import Printer
from api.octoprint_views import *

# https://docs.python.org/3/library/unittest.mock.html#where-to-patch for why it is patching "api.octoprint_views.send_failure_alert" not "app.notifications.send_failure_alert"
@patch('api.octoprint_views.send_failure_alert')
class AlertTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email='test@tsd.com')
        user.set_password('test')
        user.save()
        self.printer = Printer.objects.create(user=user)
        print = Print.objects.create(user=user, printer=self.printer, filename='test.gcode', started_at=timezone.now())
        self.printer.current_print = print
        self.printer.save()

        self.client = Client()
        self.client.login(email='test@tsd.com', password='test')

    def test_warning_once_and_cancel(self, send_failure_alert):
        response = self.client.get('/api/printers/{}/cancel_print/'.format(self.printer.id))
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'succeeded': True, 'user_credited': False})

        alert_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=True, print_paused=False)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)

        response = self.client.get('/api/printers/{}/cancel_print/'.format(self.printer.id))
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'succeeded': True, 'user_credited': True})
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at > self.printer.current_print.alerted_at)
        self.assertEqual(self.printer.current_print.alert_overwrite, Print.FAILED)

    def test_warning_once_and_acknowledge(self, send_failure_alert):
        alert_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=True, print_paused=False)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)

        response = self.client.get('/api/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'succeeded': True, 'user_credited': True})
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at > self.printer.current_print.alerted_at)
        self.assertEqual(self.printer.current_print.alert_overwrite, Print.NOT_FAILED)

    def test_warning_twice(self, send_failure_alert):
        alert_if_needed(self.printer)
        alert_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=True, print_paused=False)

    def test_warning_twice_acknowledged_in_between(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer)
            self.client.get('/api/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        alert_if_needed(self.printer)
        self.assertEqual(send_failure_alert.call_count, 2)

    def test_warning_twice_acknowledged_muted_in_between(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer)
        with patch('django.utils.timezone.now', return_value=(timezone.now() - timedelta(minutes=30))):
            self.client.get('/api/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))
            self.client.get('/api/printers/{}/mute_current_print/'.format(self.printer.id), {'mute_alert': 'true'})

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at > self.printer.current_print.alerted_at)
        self.assertEqual(self.printer.current_print.alert_overwrite, Print.NOT_FAILED)

        alert_if_needed(self.printer)
        self.assertEqual(send_failure_alert.call_count, 1)

    def test_warning_not_alerted_again_shortly_after_acknowledged(self, send_failure_alert):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        with patch('django.utils.timezone.now', return_value=one_minute_ago):
            alert_if_needed(self.printer)
            self.client.get('/api/printers/{}/resume_print/'.format(self.printer.id))

        self.printer.refresh_from_db()
        alert_if_needed(self.printer)
        self.assertEqual(send_failure_alert.call_count, 1)

    def test_error_once_and_acknowledge(self, send_failure_alert):
        pause_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=False, print_paused=True)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

        self.client.get('/api/printers/{}/cancel_print/'.format(self.printer.id))
        self.printer.refresh_from_db()
        self.assertTrue(self.printer.current_print.alert_acknowledged_at > self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_then_error(self, send_failure_alert):
        alert_if_needed(self.printer)
        send_failure_alert.assert_called_with(self.printer, is_warning=True, print_paused=False)
        pause_if_needed(self.printer)
        send_failure_alert.assert_called_with(self.printer, is_warning=False, print_paused=True)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_error_then_warning(self, send_failure_alert):
        pause_if_needed(self.printer)
        alert_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=False, print_paused=True)
        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_acknowledged_then_error(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            alert_if_needed(self.printer)
            send_failure_alert.assert_called_with(self.printer, is_warning=True, print_paused=False)
            self.client.get('/api/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer)
        send_failure_alert.assert_called_with(self.printer, is_warning=False, print_paused=True)
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNotNone(self.printer.current_print.paused_at)

    def test_warning_acknowledged_then_error_shortly_after(self, send_failure_alert):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        with patch('django.utils.timezone.now', return_value=one_minute_ago):
            alert_if_needed(self.printer)
            self.client.get('/api/printers/{}/acknowledge_alert/?alert_overwrite=NOT_FAILED'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer)
        self.assertIsNone(self.printer.current_print.alert_muted_at)

        send_failure_alert.assert_called_once_with(self.printer, is_warning=True, print_paused=False)

    def test_error_resumed_then_warning(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer)
        with patch('django.utils.timezone.now', return_value=(timezone.now() - timedelta(minutes=30))):
            send_failure_alert.assert_called_with(self.printer, is_warning=False, print_paused=True)
            self.client.get('/api/printers/{}/resume_print/'.format(self.printer.id))

        self.printer.refresh_from_db()
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at > self.printer.current_print.alerted_at)
        self.assertIsNone(self.printer.current_print.paused_at)

        alert_if_needed(self.printer)
        send_failure_alert.assert_called_with(self.printer, is_warning=True, print_paused=False)
        self.assertIsNone(self.printer.current_print.alert_muted_at)
        self.assertTrue(self.printer.current_print.alert_acknowledged_at < self.printer.current_print.alerted_at)
        self.assertIsNone(self.printer.current_print.paused_at)

    def test_error_resumed_muted_then_warning(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer)
        with patch('django.utils.timezone.now', return_value=timezone.now() - timedelta(hours=0.5)):
            self.client.get('/api/printers/{}/resume_print/'.format(self.printer.id), {'mute_alert': 'true'})

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)

        pause_if_needed(self.printer)
        self.assertIsNotNone(self.printer.current_print.alert_muted_at)

        send_failure_alert.assert_called_once_with(self.printer, is_warning=False, print_paused=True)

    def test_error_not_paused_if_confiugured_so(self, send_failure_alert):
        self.printer.action_on_failure = Printer.NONE
        self.printer.save()
        pause_if_needed(self.printer)
        send_failure_alert.assert_called_once_with(self.printer, is_warning=False, print_paused=False)

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNone(self.printer.current_print.paused_at)

    def test_error_not_paused_afer_confiugured(self, send_failure_alert):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=one_hour_ago):
            pause_if_needed(self.printer)
            send_failure_alert.assert_called_with(self.printer, is_warning=False, print_paused=True)
            self.printer.refresh_from_db()
            self.assertIsNotNone(self.printer.current_print.alerted_at)
            self.assertIsNotNone(self.printer.current_print.paused_at)

        with patch('django.utils.timezone.now', return_value=timezone.now() - timedelta(hours=0.5)):
            self.client.get('/api/printers/{}/resume_print/'.format(self.printer.id))

        self.printer.action_on_failure = Printer.NONE
        self.printer.save()

        self.printer.refresh_from_db()
        pause_if_needed(self.printer)
        send_failure_alert.assert_called_with(self.printer, is_warning=False, print_paused=False)

        self.printer.refresh_from_db()
        self.assertIsNotNone(self.printer.current_print.alerted_at)
        self.assertIsNone(self.printer.current_print.paused_at)
