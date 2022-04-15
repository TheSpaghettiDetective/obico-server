from django.test import TransactionTestCase
from unittest.mock import patch


from app.models import User, HeaterTracker, Printer, Print
from .heater_trackers import process_heater_temps


class HeaterTrackerTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create(email="a@test")
        self.printer = Printer.objects.create(user=self.user)

    def test_not_created_without_target(self):
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': None, 'offset': 0}}
        )

        self.assertIsNone(self.printer.heatertracker_set.first())

    def test_created_when_has_target(self):
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 0.0, 'offset': 0}}
        )

        self.assertEqual(self.printer.heatertracker_set.first().target, 0.0)

    def test_updated_when_target_changes(self):
        tracker = HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=0.0, reached=False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': 100.0, 'offset': 0}}
        )

        tracker.refresh_from_db()
        self.assertEqual(tracker.target, 100.0)

    def test_deleted_when_obsolete(self):
        HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=0.0, reached=False)
        HeaterTracker.objects.create(
            printer=self.printer, name='h1', target=200.0, reached=False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 50.0, 'target': None, 'offset': 0}}
            # h1 is no longer exists in data
        )

        self.assertEqual(self.printer.heatertracker_set.count(), 0)

    @patch("lib.heater_trackers.send_heater_event")
    def test_cooled_down_threshold(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=0.0, reached=False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 36.0, 'target': 0.0, 'offset': 0}}
        )

        self.assertIs(self.printer.heatertracker_set.first().reached, False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 35.0, 'target': 0.0, 'offset': 0}}
        )

        self.assertIs(self.printer.heatertracker_set.first().reached, True)

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]['event'], 'CooledDown')

    @patch("lib.heater_trackers.send_heater_event")
    def test_target_reached_delta(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=60.0, reached=False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 57.0, 'target': 60.0, 'offset': 0}}
        )

        self.assertIs(self.printer.heatertracker_set.first().reached, False)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 58.0, 'target': 60.0, 'offset': 0}}
        )

        self.assertIs(self.printer.heatertracker_set.first().reached, True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]['event'], 'ReachedTarget')

    @patch("lib.heater_trackers.send_heater_event")
    def test_no_events_after_reached(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=60.0, reached=True)

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
        self.assertIs(self.printer.heatertracker_set.first().reached, True)

    @patch("lib.heater_trackers.send_heater_event")
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

        self.assertIs(self.printer.heatertracker_set.first().reached, True)
        self.assertEqual(len(calls), 1)

    @patch("lib.heater_trackers.send_heater_event")
    def test_target_changes_and_reached_event(self, mock_send):
        calls = []

        def call(*args, **kwargs):
            calls.append((args, kwargs))

        mock_send.side_effect = call

        HeaterTracker.objects.create(
            printer=self.printer, name='h0', target=60.0, reached=True)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 70.0, 'target': 70.0, 'offset': 0}}
        )

        self.assertIs(self.printer.heatertracker_set.first().reached, True)
        self.assertEqual(len(calls), 1)

    def test_update_error_retry_cnt(self):
        ret0 = process_heater_temps(
            self.printer,
            {'h0': {'actual': 40.0, 'target': 70.0, 'offset': 0}}
        )
        self.assertEqual(ret0, 0)

        HeaterTracker.objects.all().delete()

        ret1 = process_heater_temps(
            self.printer,
            {'h0': {'actual': 70.0, 'target': 70.0, 'offset': 0}}
        )

        self.assertEqual(ret1, 1)

    def test_heater_target_is_saved_when_first_reached(self):
        print = Print.objects.create(printer=self.printer, user=self.user)
        self.printer.current_print = print
        self.printer.save()

        # very first gets reached if target is in actual+-delta
        process_heater_temps(
            self.printer,
            {'h0': {'actual': 60.0, 'target': 60.0, 'offset': 0}}
        )

        self.assertEqual(print.PrintHeaterTarget_set.first().name, 'h0')
        self.assertEqual(print.PrintHeaterTarget_set.first().target, 60.0)

        process_heater_temps(
            self.printer,
            {'h0': {'actual': 80.0, 'target': 80.0, 'offset': 0}}
        )

        self.assertEqual(print.PrintHeaterTarget_set.first().name, 'h0')
        self.assertEqual(print.PrintHeaterTarget_set.first().target, 60.0)
