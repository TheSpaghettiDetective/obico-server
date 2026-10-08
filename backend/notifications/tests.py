from unittest.mock import patch

from django.test import TestCase
from rest_framework.serializers import ValidationError

from notifications.plugins.twilio import TwillioNotificationPlugin


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
