from typing import Dict, Optional
import logging
import requests
from django.conf import settings
from rest_framework.serializers import ValidationError

from pushbullet import Pushbullet, PushbulletError, PushError  # type: ignore
from lib import syndicate

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class PushBulletNotificationPlugin(BaseNotificationPlugin):

    def validate_config(self, data: Dict) -> Dict:
        if 'access_token' in data:
            access_token = data['access_token'].strip()
            if access_token:
                try:
                    Pushbullet(access_token)
                except PushbulletError:
                    raise ValidationError('Invalid pushbullet access token.')
            return {'access_token': access_token}
        raise ValidationError('access_token is missing from config')

    def get_access_token_from_config(self, config: Dict) -> str:
        if config and 'access_token' in config:
            return config['access_token']
        return ''

    def call_pushbullet(
        self,
        access_token: str,
        title: str,
        body: str,
        link: str,
        file_url: str,
    ) -> None:
        pb = Pushbullet(access_token)
        try:
            if not settings.SITE_IS_PUBLIC:
                pb.upload_file(requests.get(file_url).content, 'Snapshot.jpg')
        except:
            pass

        if file_url:
            pb.push_file(file_url=file_url, file_name="Snapshot.jpg", file_type="image/jpeg", body=body, title=title)
        else:
            pb.push_link(title, link, body)


    def send_failure_alert(self, context: FailureAlertContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        link = syndicate.build_full_url_for_syndicate('/', context.user.syndicate_name),
        title = self.get_failure_alert_title(context=context, link=link)
        text = self.get_failure_alert_text(context=context, link=link)
        if not title or not text:
            return

        self.call_pushbullet(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            file_url=context.img_url,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        title = self.get_printer_notification_title(context=context)
        text = self.get_printer_notification_text(context=context)
        if not text or not title:
            return

        link = syndicate.build_full_url_for_syndicate('/', context.user.syndicate_name),

        self.call_pushbullet(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            file_url=context.img_url,
        )

    def send_test_message(self, context: TestMessageContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        link = syndicate.build_full_url_for_syndicate('/', context.user.syndicate_name),
        self.call_pushbullet(
            access_token=access_token,
            title='Test Notification',
            body='It works',
            link=link,
            file_url='',
        )


def __load_plugin__():
    return PushBulletNotificationPlugin()
