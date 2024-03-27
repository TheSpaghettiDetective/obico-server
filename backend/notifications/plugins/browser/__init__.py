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

    def send_notification(
        self,
        config: Dict,
        title: str,
        message: str,
        link: str,
        tag: str,
        image: str,
    ) -> None:
        vapid_subject = os.environ.get('VAPID_SUBJECT')
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
        if not vapid_subject or not vapid_private_key or not config['subscriptions']:
            LOGGER.warn("Missing configuration, won't send notifications to browser")
            return

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
                        "image": image,
                        "url": link,
                        "tag": tag,
                    }),
                    vapid_private_key=vapid_private_key,
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
        link = site.build_full_url(f'/printers/{context.printer.id}/control')
        title = self.get_failure_alert_title(context=context, link=link)
        text = self.get_failure_alert_text(context=context, link=link)
        if not title or not text:
            return

        self.send_notification(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            tag=context.printer.name,
            image=context.img_url,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        title = self.get_printer_notification_title(context=context)
        text = self.get_printer_notification_text(context=context)
        if not text or not title:
            return

        link = site.build_full_url(f'/printers/{context.printer.id}/control')

        self.send_notification(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            tag=context.printer.name,
            image=context.img_url,
        )

    def send_test_message(self, context: TestMessageContext) -> None:
        self.send_notification(
            config=context.config,
            title='Test Notification',
            message='It works!',
            image="http://localhost:3334/media/tsd-pics/snapshots/1/1711225060.616871_rotated.jpg?digest=YidtXHg5MEJceDA3XHgxMlx4ZTl2XHgwNFx4OWV7XHg5Y3JjXHg5NGczP1x4ODVceGJhXHhhMFx4MTBfXHgxZVx4YWRceGY2XHhjNlx4ZTZceGI3XHg5ZDdsXHIn",
            link="http://localhost:3334/printers/1/control",
            tag="printer1"
        )


def __load_plugin__():
    return BrowserNotificationPlugin()
