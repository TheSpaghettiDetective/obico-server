from typing import Dict, Optional, Any
import logging
import io
import os
from enum import IntEnum
from rest_framework.serializers import ValidationError
from pywebpush import webpush, WebPushException
import json
from lib import site as site

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class BrowserException(Exception):
    pass

class BrowserNotificationPlugin(BaseNotificationPlugin):

    def validate_config(self, data: Dict) -> Dict:
        if 'subscriptions' in data:
            return {'subscriptions': data['subscriptions']}
        raise ValidationError('subscriptions are missing from config')

    def env_vars(self) -> Dict:
        return {
            'VAPID_PUBLIC_KEY': {
                'is_required': True,
                'is_set': 'VAPID_PUBLIC_KEY' in os.environ,
                'value': os.environ.get('VAPID_PUBLIC_KEY'),
            },
        }

    def i(self, s: str) -> str:
        return f"<i>{s}</i>"

    def b(self, s: str):
        return f"<b>{s}</b>"

    def u(self, s: str):
        return f"<u>{s}</u>"

    def send_notification(
        self,
        config: Dict,
        title: str,
        message: str,
        priority: Optional[BrowserPriority] = None,
        file_content: Optional[bytes] = None,
        timeout: float = 5.0,
    ) -> None:
        vapid_subject = os.environ.get('VAPID_SUBJECT')

        for subscription in config['subscriptions']:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription['endpoint'],
                        "keys": subscription['keys'],
                    },
                    data=json.dumps({
                        "title": title,
                        "message": message,
                    }),
                    vapid_private_key=os.environ.get('VAPID_PRIVATE_KEY'),
                    vapid_claims={
                        "sub": f'mailto:{vapid_subject}',
                    }
                )
            except WebPushException as ex:
                LOGGER.warn("Failed to send browser push notification: {}", repr(ex))
                # Mozilla returns additional information in the body of the response.
                if ex.response and ex.response.json():
                    extra = ex.response.json()
                    LOGGER.warn("Remote service replied with a {}:{}, {}",
                        extra.code,
                        extra.errno,
                        extra.message
                    )

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        # TODO

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        # TODO

    def send_test_message(self, context: TestMessageContext) -> None:
        self.send_notification(
            config=context.config,
            title='Test Notification',
            message='It works!',
        )


def __load_plugin__():
    return BrowserNotificationPlugin()
