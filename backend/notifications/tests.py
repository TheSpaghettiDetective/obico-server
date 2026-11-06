from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.serializers import ValidationError

from notifications.plugins.discord import DiscordNotificationPlugin
from notifications.plugins.twilio import TwillioNotificationPlugin


# TWILIO_COUNTRY_CODES restricts which destination countries Twilio is used for;
# the empty default in settings places no restriction, so the Finland asserts need
# a serviced list that excludes it.
@override_settings(TWILIO_COUNTRY_CODES=[1])
class TwilioCountryCodeTestCase(TestCase):

    def setUp(self):
        self.plugin = TwillioNotificationPlugin()

    def test_validate_config_rejects_finland_country_code(self):
        with self.assertRaises(ValidationError):
            self.plugin.validate_config({
                'phone_country_code': '358',
                'phone_number': '401234567',
            })

    @patch('notifications.plugins.twilio.Client')
    def test_send_sms_skips_twilio_for_existing_finland_number(self, mock_client_cls):
        self.plugin.send_sms(body='test', to_number='+358401234567')

        mock_client_cls.assert_not_called()


class TwilioNumberNormalizationTestCase(TestCase):

    def setUp(self):
        self.plugin = TwillioNotificationPlugin()

    @patch.dict('os.environ', {'TWILIO_ACCOUNT_SID': 'sid', 'TWILIO_AUTH_TOKEN': 'token', 'TWILIO_FROM_NUMBER': '+15550100'})
    @patch('notifications.plugins.twilio.Client')
    def test_send_sms_drops_the_national_trunk_prefix_kept_after_the_country_code(self, mock_client_cls):
        self.plugin.send_sms(body='test', to_number='+4407786011234')

        mock_client_cls.return_value.messages.create.assert_called_once_with(
            body='test', to='+447786011234', from_='+15550100')

    @patch.dict('os.environ', {'TWILIO_ACCOUNT_SID': 'sid', 'TWILIO_AUTH_TOKEN': 'token', 'TWILIO_FROM_NUMBER': '+15550100'})
    @patch('notifications.plugins.twilio.Client')
    def test_send_sms_leaves_a_normal_number_unchanged(self, mock_client_cls):
        self.plugin.send_sms(body='test', to_number='+14155550132')

        mock_client_cls.return_value.messages.create.assert_called_once_with(
            body='test', to='+14155550132', from_='+15550100')


class DiscordWebhookUrlTestCase(TestCase):

    def setUp(self):
        self.plugin = DiscordNotificationPlugin()

    def test_validate_config_rejects_text_that_is_not_a_webhook_url(self):
        for bad in ('3d Ender printer', 'https://example.com/api/webhooks/1/abc', 'http://discord.com/api/webhooks/1/abc',
                    'https://discord.com/api/webhooks/abc/def'):
            with self.subTest(url=bad):
                with self.assertRaises(ValidationError):
                    self.plugin.validate_config({'webhook_url': bad})

    def test_validate_config_accepts_discord_webhook_urls(self):
        for good in ('https://discord.com/api/webhooks/123456/abc-DEF_123',
                     'https://discordapp.com/api/webhooks/123456/abc',
                     'https://canary.discord.com/api/v10/webhooks/123456/abc',
                     '  https://discord.com/api/webhooks/123456/abc  '):
            with self.subTest(url=good):
                self.assertEqual(
                    self.plugin.validate_config({'webhook_url': good})['webhook_url'], good.strip())

    def test_validate_config_still_allows_clearing_the_url(self):
        self.assertEqual(self.plugin.validate_config({'webhook_url': ''}), {'webhook_url': ''})
