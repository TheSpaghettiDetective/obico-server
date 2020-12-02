from django.test import TestCase
from unittest.mock import patch


from .models import User, HeaterTrackers, Printer
from .heater_trackers import process_heater_temps, parse_trackers


class HeaterTrackerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="a@test")
        self.printer = Printer.objects.create(user=self.user)

    def test_not_created_without_target(self):
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': None, 'offset': 0}}
        )

        trackers = HeaterTrackers.objects.get(printer=self.printer)
        self.assertEqual(len(trackers.data), 0)

    def test_created_when_has_target(self):
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 0.0, 'offset': 0}}
        )

        trackers = HeaterTrackers.objects.get(printer=self.printer)
        self.assertEqual(trackers.data[0]['target'], 0.0)

    def test_printer_heatertracekrs_data_attr_updates(self):
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 0.0, 'offset': 0}}
        )

        self.assertEqual(self.printer.heatertrackers.data[0]['target'], 0.0)

    def test_updated_when_target_changes(self):
        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[{'name': 'h0', 'target': 0.0, 'reached': False}])

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 100.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertEqual(trackers.data[0]['target'], 100.0)

    def test_deleted_when_obsolete(self):
        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[
                {'name': 'h0', 'target': 0.0, 'reached': False},
                {'name': 'h1', 'target': 200.0, 'reached': False}
            ]
        )

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': None, 'offset': 0}}
            # h1 is no longer exists in data
        )

        trackers.refresh_from_db()
        self.assertEqual(len(trackers.data), 0)

    @patch("app.heater_trackers.send_heater_event")
    def test_cooled_down_threshold(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[{'name': 'h0', 'target': 0.0, 'reached': False}])

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 36.0, 'target': 0.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 35.0, 'target': 0.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], True)

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]['event'], 'cooled down')

    @patch("app.heater_trackers.send_heater_event")
    def test_target_reached_delta(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[{'name': 'h0', 'target': 60.0, 'reached': False}]
        )

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 57.0, 'target': 60.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 58.0, 'target': 60.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]['event'], 'target reached')

    @patch("app.heater_trackers.send_heater_event")
    def test_no_events_after_reached(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[{'name': 'h0', 'target': 60.0, 'reached': True}]
        )

        # -delta
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 58.0, 'target': 60.0, 'offset': 0}}
        )

        # +delta
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 62.0, 'target': 60.0, 'offset': 0}}
        )

        # -whatever
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 70.0, 'target': 60.0, 'offset': 0}}
        )

        # +whatever
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 60.0, 'offset': 0}}
        )

        self.assertEqual(len(calls), 0)
        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], True)

    @patch("app.heater_trackers.send_heater_event")
    def test_first_seen_reached_event(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        # very first gets reached if target is in actual+-delta
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 60.0, 'target': 60.0, 'offset': 0}}
        )

        trackers = HeaterTrackers.objects.get(printer=self.printer)
        self.assertIs(trackers.data[0]['reached'], True)
        self.assertEqual(len(calls), 1)

    @patch("app.heater_trackers.send_heater_event")
    def test_target_changes_and_reached_event(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        trackers = HeaterTrackers.objects.create(
            printer=self.printer,
            data=[{'name': 'h0', 'target': 60.0, 'reached': True}])

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 70.0, 'target': 70.0, 'offset': 0}}
        )

        trackers.refresh_from_db()
        self.assertIs(trackers.data[0]['reached'], True)

        self.assertEqual(len(calls), 1)

    def test_update_error_retry_cnt(self):
        ret0 = process_heater_temps(
            self.printer,
            {'h0': {'actual': 40.0, 'target': 70.0, 'offset': 0}}
        )
        self.assertEqual(ret0, 0)

        HeaterTrackers.objects.all().delete()

        ret1 = process_heater_temps(
            self.printer,
            {'h0': {'actual': 70.0, 'target': 70.0, 'offset': 0}}
        )

        self.assertEqual(ret1, 1)
