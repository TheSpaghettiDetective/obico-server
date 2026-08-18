from django.test import TestCase, TransactionTestCase, override_settings
from unittest.mock import patch


from app.models import User, HeaterTracker, Printer, Print
from .heater_trackers import process_heater_temps
from .url_signing import HmacSignedUrl, new_signed_url, rewrite_url_origin
from .turn import turn_config


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


class NewSignedUrlTestCase(TestCase):

    def test_signed_url_keeps_scheme_host_and_path(self):
        signed = new_signed_url('http://old-host:3334/media/tsd-timelapses/private/1.mp4?digest=stale')

        self.assertTrue(signed.startswith('http://old-host:3334/media/tsd-timelapses/private/1.mp4?digest='))
        self.assertTrue(HmacSignedUrl(signed).is_authorized())


class RewriteUrlOriginTestCase(TestCase):

    def test_matching_origin_is_rewritten_and_rest_of_url_is_preserved(self):
        signed = new_signed_url('http://old-host:3334/media/tsd-timelapses/private/1.mp4')

        rewritten = rewrite_url_origin(signed, 'http://old-host:3334', 'https://new-host')

        self.assertEqual(rewritten, signed.replace('http://old-host:3334', 'https://new-host'))
        self.assertTrue(HmacSignedUrl(rewritten).is_authorized())

    def test_other_origin_is_untouched(self):
        url = 'https://storage.example.com/bucket/1.mp4?sig=provider'

        self.assertEqual(rewrite_url_origin(url, 'http://old-host:3334', 'https://new-host'), url)

    def test_relative_url_is_untouched(self):
        url = '/media/g_code_files/1.gcode?digest=abc'

        self.assertEqual(rewrite_url_origin(url, 'http://old-host:3334', 'https://new-host'), url)

    def test_origin_matching_ignores_case_and_trailing_slash(self):
        rewritten = rewrite_url_origin(
            'http://OLD-Host:3334/media/1.mp4?digest=abc', 'http://old-host:3334/', 'https://New-Host/')

        self.assertEqual(rewritten, 'https://new-host/media/1.mp4?digest=abc')

    def test_invalid_origin_is_rejected(self):
        with self.assertRaises(ValueError):
            rewrite_url_origin('http://old-host:3334/media/1.mp4', 'old-host:3334', 'https://new-host')
        with self.assertRaises(ValueError):
            rewrite_url_origin('http://old-host:3334/media/1.mp4', 'http://old-host:3334', 'https://new-host/media')


class TurnConfigTestCase(TestCase):

    @override_settings(TURN_SERVER=None)
    def test_none_when_not_configured(self):
        self.assertIsNone(turn_config('web', 60))

    @override_settings(TURN_SERVER='turn.example.com', TURN_PORT=3478, TURN_TRANSPORTS=['udp', 'tcp'],
                       TURN_SECRET=None, TURN_USERNAME='alice', TURN_CREDENTIAL='s3cret')
    def test_static_credentials(self):
        config = turn_config('web', 60)

        self.assertEqual(config['server'], 'turn.example.com')
        self.assertEqual(config['port'], 3478)
        self.assertEqual(config['transports'], ['udp', 'tcp'])
        self.assertEqual(config['username'], 'alice')
        self.assertEqual(config['credential'], 's3cret')
        self.assertIsNone(config['expires_at'])

    @override_settings(TURN_SERVER='turn.example.com', TURN_PORT=3478, TURN_TRANSPORTS=['udp'],
                       TURN_SECRET='shared', TURN_USERNAME=None, TURN_CREDENTIAL=None)
    @patch('lib.turn.time.time', return_value=1_700_000_000)
    def test_secret_credentials(self, _):
        config = turn_config('printer:42', 3600)

        self.assertEqual(config['expires_at'], 1_700_003_600)
        self.assertEqual(config['username'], '1700003600:printer:42')
        # base64(HMAC-SHA1('shared', '1700003600:printer:42')), as a TURN server in REST API mode verifies it
        self.assertEqual(config['credential'], 'XW1H4eU4sQt6tTavEjhfZAlsCZM=')
        self.assertEqual(config['transports'], ['udp'])

    @override_settings(TURN_SERVER='turn.example.com', TURN_SECRET='shared', TURN_USERNAME=None, TURN_CREDENTIAL=None)
    def test_secret_credentials_differ_per_label(self):
        self.assertNotEqual(turn_config('a', 60)['credential'], turn_config('b', 60)['credential'])
