"""Paid or metered features must not be reachable for free: AI detection, hour credits, tunnel usage, SMS, share links."""
from unittest.mock import patch, MagicMock
from datetime import timedelta
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from app.models import Printer, Print, PrintShotFeedback, PrinterPrediction, SharedResource, NotificationSetting, User
from rest_framework.exceptions import PermissionDenied
from api.octoprint_views import OctoPrintPicView
from notifications.plugin import TestMessageContext, UserContext
from notifications.plugins.twilio import TwillioNotificationPlugin
from api.consumers import SharedWebConsumer, JanusSharedWebConsumer
from lib import cache
from .tests import setup_syndicate


LOCAL_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
TEST_MESSAGES_PER_HOUR = 10


def printers_behind_share_link(token):
    """The printer each share-link websocket (status, video) connects to, as a list; a refusal raises."""
    printers = []
    for consumer_class in (SharedWebConsumer, JanusSharedWebConsumer):
        consumer = consumer_class.__new__(consumer_class)
        consumer.scope = {'url_route': {'kwargs': {'share_token': token}}}
        printers.append(consumer.get_printer())
    return printers


def assert_refused(test, token):
    for consumer_class in (SharedWebConsumer, JanusSharedWebConsumer):
        consumer = consumer_class.__new__(consumer_class)
        consumer.scope = {'url_route': {'kwargs': {'share_token': token}}}
        # Printer.DoesNotExist is how every websocket consumer signals an authentication failure
        with test.assertRaises(Printer.DoesNotExist):
            consumer.get_printer()


def make_user(email, is_pro=True):
    user = User.objects.create(email=email, syndicate=setup_syndicate(), is_pro=is_pro)
    client = Client()
    client.force_login(user)
    return user, client


@override_settings(SITE_ID=1)
@patch('api.viewsets.celery_app')
class PrintShotFeedbackCreditTestCase(TestCase):

    def setUp(self):
        self.user, self.client = make_user('feedback@example.invalid')
        self.printer = Printer.objects.create(user=self.user, name='p')
        self.print = Print.objects.create(user=self.user, printer=self.printer, filename='a.gcode', started_at=timezone.now(), ext_id=1)
        self.shot = PrintShotFeedback.objects.create(print=self.print, image_url='https://example.invalid/1.jpg')

    def url(self, shot):
        return f'/api/v1/printshotfeedbacks/{shot.id}/?print_id={self.print.id}'

    def test_an_update_that_answers_nothing_is_not_credited(self, celery_app):
        response = self.client.patch(self.url(self.shot), '{}', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['credited_dhs'], 0)
        celery_app.send_task.assert_not_called()
        self.shot.refresh_from_db()
        self.assertIsNone(self.shot.answered_at)

    def test_a_null_answer_is_not_credited(self, celery_app):
        response = self.client.patch(self.url(self.shot), json.dumps({'answer': None}), content_type='application/json')

        self.assertEqual(response.json()['credited_dhs'], 0)
        celery_app.send_task.assert_not_called()

    def test_answering_the_last_shot_is_credited_once_per_print(self, celery_app):
        response = self.client.put(self.url(self.shot), json.dumps({'answer': 'LOOKS_OK'}), content_type='application/json')

        self.assertEqual(response.json()['credited_dhs'], 2)
        self.assertEqual(response.json()['instance']['answer'], 'LOOKS_OK')
        celery_app.send_task.assert_called_once()
        self.assertEqual(celery_app.send_task.call_args.kwargs['args'][3], f'ff:p:{self.print.id}')

    def test_answering_while_other_shots_are_unanswered_is_not_credited(self, celery_app):
        PrintShotFeedback.objects.create(print=self.print, image_url='https://example.invalid/2.jpg')

        response = self.client.put(self.url(self.shot), json.dumps({'answer': 'LOOKS_BAD'}), content_type='application/json')

        self.assertEqual(response.json()['credited_dhs'], 0)
        celery_app.send_task.assert_not_called()

    def test_an_invalid_answer_is_refused_and_not_credited(self, celery_app):
        response = self.client.put(self.url(self.shot), json.dumps({'answer': 'NOT_A_CHOICE'}), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        celery_app.send_task.assert_not_called()


class TunnelResponseRefTestCase(SimpleTestCase):

    @patch('lib.cache.BREDIS')
    def test_a_ref_the_server_did_not_issue_is_refused(self, bredis):
        for ref in ('stats.209901', 'etags.1./', '', None, 5, ['v2.']):
            with self.assertRaises(ValueError):
                cache.octoprinttunnel_http_response_set(ref, {'response': {}})
        bredis.pipeline.assert_not_called()

    @patch('lib.cache.BREDIS')
    def test_a_server_issued_ref_is_stored(self, bredis):
        pipe = bredis.pipeline.return_value.__enter__.return_value

        cache.octoprinttunnel_http_response_set('v2.12.GET.1700000000.5./api/version', {'response': {}})

        pipe.lpush.assert_called_once()
        self.assertEqual(pipe.lpush.call_args.args[0], 'octoprinttunnel.v2.12.GET.1700000000.5./api/version')


@override_settings(SITE_ID=1, CACHES=LOCAL_CACHE)
@patch('api.viewsets.handler.send_test_message')
class NotificationTestMessageLimitTestCase(TestCase):

    def setUp(self):
        from django.core.cache import cache as django_cache
        django_cache.clear()
        self.user, self.client = make_user('sms@example.invalid', is_pro=False)
        self.setting = NotificationSetting.objects.create(
            user=self.user, name='twilio', config_json=json.dumps({'phone_country_code': '+1', 'phone_number': '2025550123'}))

    def press_test(self):
        return self.client.post(f'/api/v1/notification_settings/{self.setting.id}/send_test_message/')

    def test_test_messages_are_limited_per_account(self, send_test_message):
        for _ in range(TEST_MESSAGES_PER_HOUR):
            self.assertEqual(self.press_test().status_code, 200)

        self.assertEqual(self.press_test().status_code, 429)
        self.assertEqual(send_test_message.call_count, TEST_MESSAGES_PER_HOUR)

    def test_the_limit_is_per_account(self, send_test_message):
        for _ in range(TEST_MESSAGES_PER_HOUR):
            self.press_test()

        other_user, other_client = make_user('sms2@example.invalid')
        other_setting = NotificationSetting.objects.create(user=other_user, name='twilio', config_json='{}')
        response = other_client.post(f'/api/v1/notification_settings/{other_setting.id}/send_test_message/')
        self.assertEqual(response.status_code, 200)


@override_settings(SITE_ID=1)
class ShareLinkPlanTestCase(TestCase):

    def setUp(self):
        self.pro_user, self.pro_client = make_user('pro@example.invalid', is_pro=True)
        self.free_user, self.free_client = make_user('free@example.invalid', is_pro=False)

    def share(self, user, token, **printer_fields):
        printer = Printer.objects.create(user=user, name='p', **printer_fields)
        SharedResource.objects.create(printer=printer, share_token=token)
        return printer

    def test_a_paid_plan_users_link_reaches_the_printer(self):
        printer = self.share(self.pro_user, 'pro-token')
        self.assertEqual(printers_behind_share_link('pro-token'), [printer, printer])
        self.assertEqual(Client().get('/printers/share_token/pro-token/').status_code, 200)

    def test_a_free_plan_users_link_is_refused_like_the_share_page(self):
        self.share(self.free_user, 'free-token')
        assert_refused(self, 'free-token')
        self.assertEqual(Client().get('/printers/share_token/free-token/').status_code, 404)

    def test_an_archived_printers_link_is_refused_like_the_share_page(self):
        self.share(self.pro_user, 'archived-token', archived_at=timezone.now())
        assert_refused(self, 'archived-token')
        self.assertEqual(Client().get('/printers/share_token/archived-token/').status_code, 404)

    def test_an_unknown_token_is_an_auth_failure(self):
        assert_refused(self, 'no-such-token')

    def test_a_free_plan_user_cannot_create_a_link(self):
        printer = Printer.objects.create(user=self.free_user, name='p')
        response = self.free_client.post(f'/api/v1/sharedresources/?printer_id={printer.id}')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SharedResource.objects.filter(printer=printer).exists())

    def test_a_paid_plan_user_can_create_a_link(self):
        printer = Printer.objects.create(user=self.pro_user, name='p')
        response = self.pro_client.post(f'/api/v1/sharedresources/?printer_id={printer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


@override_settings(SITE_ID=1, MIN_DETECTION_INTERVAL=10, ML_API_HOST='http://ml-api.example.invalid')
@patch('app.models.other_models.cache.print_num_predictions_incr')
@patch('app.models.other_models.cache.printer_detection_claim', return_value=0, create=True)
class DetectionRulesTestCase(TestCase):
    """The printer agent's pictures and the API for apps follow one set of detection rules."""

    def setUp(self):
        self.user, self.client = make_user('detect@example.invalid', is_pro=False)
        self.user.dh_balance = 5
        self.user.save()
        self.printer = Printer.objects.create(user=self.user, name='p', auth_token='detect-token')
        self.print = Print.objects.create(user=self.user, printer=self.printer, filename='a.gcode', started_at=timezone.now(), ext_id=1)
        self.printer.current_print = self.print
        self.printer.save()
        self.last_detection_ago(timedelta(minutes=1))

    def last_detection_ago(self, ago):
        PrinterPrediction.objects.get_or_create(printer=self.printer)
        PrinterPrediction.objects.filter(printer=self.printer).update(updated_at=timezone.now() - ago)

    def fresh_printer(self):
        return Printer.objects.select_related('current_print', 'user').get(id=self.printer.id)

    def test_an_allowed_detection_is_counted_toward_the_print(self, claim, incr):
        prediction, refusal = self.fresh_printer().start_detection()

        self.assertIsNone(refusal)
        self.assertEqual(prediction.printer_id, self.printer.id)
        incr.assert_called_once_with(self.print.id)

    def test_no_detection_while_off_out_of_hours_or_muted(self, claim, incr):
        cases = (
            ({'watching_enabled': False}, {}, {}, 'AI failure detection is disabled'),
            ({}, {'dh_balance': -1}, {}, 'You have run out of AI Detection Hours'),
            ({}, {}, {'alert_muted_at': timezone.now()}, 'Alerts are muted for current print'),
        )
        for printer_fields, user_fields, print_fields, reason in cases:
            Printer.objects.filter(id=self.printer.id).update(**{'watching_enabled': True, **printer_fields})
            User.objects.filter(id=self.user.id).update(**{'dh_balance': 5, **user_fields})
            Print.objects.filter(id=self.print.id).update(**{'alert_muted_at': None, **print_fields})

            _, refusal = self.fresh_printer().start_detection()

            self.assertEqual(refusal.reason, reason)
        incr.assert_not_called()
        claim.assert_not_called()

    def test_no_detection_within_the_interval(self, claim, incr):
        self.last_detection_ago(timedelta(seconds=3))

        _, refusal = self.fresh_printer().start_detection()

        self.assertIsNone(refusal.reason)
        self.assertAlmostEqual(refusal.wait_secs, 7, delta=1)
        incr.assert_not_called()

    def test_of_requests_arriving_together_only_the_claiming_one_runs(self, claim, incr):
        claim.return_value = 9

        _, refusal = self.fresh_printer().start_detection()

        self.assertEqual(refusal.wait_secs, 9)
        incr.assert_not_called()

    def predict(self, ml_get):
        ml_get.return_value.json.return_value = {'detections': []}
        return self.client.post(f'/api/v1/printers/{self.printer.id}/predict/', {'img': SimpleUploadedFile('a.jpg', b'jpg', content_type='image/jpeg')})

    @patch('api.viewsets.requests.get')
    @patch('api.viewsets.save_file_obj', return_value=('http://internal/a.jpg', 'http://external/a.jpg'))
    @patch('api.viewsets.send_status_to_web')
    def test_api_refuses_with_the_reason_when_out_of_hours(self, send_status, save_file, ml_get, claim, incr):
        User.objects.filter(id=self.user.id).update(dh_balance=-1)

        response = self.predict(ml_get)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], 'You have run out of AI Detection Hours')
        ml_get.assert_not_called()
        save_file.assert_not_called()

    @patch('api.viewsets.requests.get')
    @patch('api.viewsets.save_file_obj', return_value=('http://internal/a.jpg', 'http://external/a.jpg'))
    @patch('api.viewsets.send_status_to_web')
    def test_api_refuses_a_detection_that_comes_too_soon(self, send_status, save_file, ml_get, claim, incr):
        self.last_detection_ago(timedelta(seconds=3))

        response = self.predict(ml_get)

        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)
        ml_get.assert_not_called()
        incr.assert_not_called()

    @patch('api.viewsets.requests.get')
    @patch('api.viewsets.save_file_obj', return_value=('http://internal/a.jpg', 'http://external/a.jpg'))
    @patch('api.viewsets.send_status_to_web')
    def test_api_runs_and_counts_an_allowed_detection(self, send_status, save_file, ml_get, claim, incr):
        response = self.predict(ml_get)

        self.assertEqual(response.status_code, 200)
        ml_get.assert_called_once()
        incr.assert_called_once_with(self.print.id)

    @patch('api.octoprint_views.importlib')
    def test_agent_pictures_follow_the_same_rules(self, importlib, claim, incr):
        import_module = importlib.import_module
        view = OctoPrintPicView()
        with patch.object(Printer, 'actively_printing', return_value=True):
            User.objects.filter(id=self.user.id).update(dh_balance=-1)
            self.assertFalse(view.detect_if_needed(self.fresh_printer(), None, 'pic', 'http://internal/a.jpg'))

            User.objects.filter(id=self.user.id).update(dh_balance=5)
            self.last_detection_ago(timedelta(seconds=3))
            self.assertFalse(view.detect_if_needed(self.fresh_printer(), None, 'pic', 'http://internal/a.jpg'))
            import_module.assert_not_called()
            incr.assert_not_called()

            self.last_detection_ago(timedelta(minutes=1))
            import_module.return_value.detect.return_value = {'decision': {'should_pause': False, 'should_alert': False}}
            self.assertTrue(view.detect_if_needed(self.fresh_printer(), None, 'pic', 'http://internal/a.jpg'))
            incr.assert_called_once_with(self.print.id)


class SmsTestMessagePlanTestCase(SimpleTestCase):

    def context(self, is_pro):
        user = UserContext(id=1, email='sms@example.invalid', syndicate_name='base', first_name='', last_name='',
                           unsub_token='', dh_balance=0, is_pro=is_pro)
        return TestMessageContext(config={'phone_country_code': '+1', 'phone_number': '2025550123'}, user=user, extra_context={})

    @patch.object(TwillioNotificationPlugin, 'send_sms')
    def test_a_free_plan_account_cannot_send_an_sms_test(self, send_sms):
        with self.assertRaises(PermissionDenied):
            TwillioNotificationPlugin().send_test_message(self.context(is_pro=False))
        send_sms.assert_not_called()

    @patch.object(TwillioNotificationPlugin, 'send_sms')
    def test_a_paid_plan_account_can_send_an_sms_test(self, send_sms):
        TwillioNotificationPlugin().send_test_message(self.context(is_pro=True))
        send_sms.assert_called_once()


@override_settings(SITE_ID=1, CACHES=LOCAL_CACHE)
@patch('twilio.rest.api.v2010.account.message.MessageList.create')
class SmsTestMessageAnswerTestCase(TestCase):
    """The test-message answer says "sent" only when the SMS was handed to Twilio."""

    def press_test(self, config):
        from django.core.cache import cache as django_cache
        django_cache.clear()
        user, client = make_user('sms-answer@example.invalid', is_pro=True)
        setting = NotificationSetting.objects.create(user=user, name='twilio', config_json=json.dumps(config))
        return client.post(f'/api/v1/notification_settings/{setting.id}/send_test_message/')

    def test_a_saved_number_without_a_plus_is_not_reported_as_sent(self, create):
        response = self.press_test({'phone_country_code': '1', 'phone_number': '2025550123'})
        self.assertEqual((response.status_code, response.json()['status']), (418, 'error'))
        create.assert_not_called()

    def test_a_cleared_number_is_not_reported_as_sent(self, create):
        response = self.press_test({'phone_country_code': '', 'phone_number': ''})
        self.assertEqual((response.status_code, response.json()['status']), (418, 'error'))
        create.assert_not_called()

    @patch.dict('os.environ', {'TWILIO_ACCOUNT_SID': 'sid', 'TWILIO_AUTH_TOKEN': 'token', 'TWILIO_FROM_NUMBER': '+15550100'})
    def test_a_good_number_is_sent(self, create):
        response = self.press_test({'phone_country_code': '+1', 'phone_number': '2025550123'})
        self.assertEqual((response.status_code, response.json()['status']), (200, 'sent'))
        create.assert_called_once()
