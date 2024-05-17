from typing import Dict, Set
import logging
import phonenumbers  # type: ignore
from twilio.rest import Client  # type: ignore
from django.conf import settings
import os
from rest_framework.serializers import ValidationError

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    TestMessageContext,
    Feature,
)
from lib import syndicate

LOGGER = logging.getLogger(__file__)

TWILIO_ENABLED = os.environ.get('TWILIO_ACCOUNT_SID') and os.environ.get('TWILIO_AUTH_TOKEN') and os.environ.get('TWILIO_FROM_NUMBER')

def int_with_default(v, default):
    try:
        return int(v)
    except ValueError:
        return default


class TwillioNotificationPlugin(BaseNotificationPlugin):

    def supported_features(self) -> Set[Feature]:
        return {
            Feature.notify_on_failure_alert,
        }

    def env_vars(self) -> Dict:
        return {
            'TWILIO_ACCOUNT_SID': {
                'is_required': True,
                'is_set': 'TWILIO_ACCOUNT_SID' in os.environ,
                'value': os.environ.get('TWILIO_ACCOUNT_SID'),
            },
            'TWILIO_AUTH_TOKEN': {
                'is_required': True,
                'is_set': 'TWILIO_AUTH_TOKEN' in os.environ,
            },
            'TWILIO_FROM_NUMBER': {
                'is_required': True,
                'is_set': 'TWILIO_FROM_NUMBER' in os.environ,
            },
        }

    def get_number_from_config(self, config: Dict) -> str:
        return (config.get('phone_country_code') or '') + (config.get('phone_number') or '')

    def send_sms(self, body: str, to_number: str):
        twilio_client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        from_number = os.environ.get('TWILIO_FROM_NUMBER')

        twilio_client.messages.create(body=body, to=to_number, from_=from_number)

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        if not TWILIO_ENABLED or not context.user.is_pro:
            LOGGER.warn("Twilio settings are missing. Ignored send requests")
            return

        to_number = self.get_number_from_config(context.config)
        link = syndicate.build_full_url_for_syndicate('/printers/', context.user.syndicate_name)
        text = self.get_failure_alert_text(context=context, link=link)
        if not text or not to_number:
            return

        return self.send_sms(body=text, to_number=to_number)

    def send_test_message(self, context: TestMessageContext) -> None:
        to_number = self.get_number_from_config(context.config)
        self.send_sms(
            body='Obico App Test Notification - It works!',
            to_number=to_number,
        )

    def validate_phone_country_code(self, phone_country_code: str) -> str:
        if phone_country_code:
            phone_country_code = phone_country_code.strip().replace('+', '')

            code = int_with_default(phone_country_code, None)
            if (
                settings.TWILIO_COUNTRY_CODES and
                (code is None or code not in settings.TWILIO_COUNTRY_CODES)
            ):
                raise ValidationError({"phone_country_code": "Oops, we don't send SMS to this country code"})

            if not phone_country_code.startswith('+'):
                phone_country_code = '+' + phone_country_code

        return phone_country_code

    def validate_config(self, data: Dict) -> Dict:
        if 'phone_country_code' in data:
            data['phone_country_code'] = self.validate_phone_country_code(data['phone_country_code'])

        if 'phone_number' in data and not data['phone_number']:
            data['phone_country_code'] = ''
            data['phone_number'] = ''

        elif 'phone_number' in data or 'phone_country_code' in data:
            if 'phone_number' in data and 'phone_country_code' in data:
                phone_number = data['phone_country_code'] + data['phone_number']
                try:
                    phone_number = phonenumbers.parse(phone_number, None)
                    if not phonenumbers.is_valid_number(phone_number):
                        raise ValidationError({'phone_number': 'Invalid phone number'})
                except phonenumbers.NumberParseException as e:
                    raise ValidationError({'phone_number': e})
            else:
                raise ValidationError('Both phone_number and phone_country_code need to be present.')

        return data


def __load_plugin__():
    return TwillioNotificationPlugin()
