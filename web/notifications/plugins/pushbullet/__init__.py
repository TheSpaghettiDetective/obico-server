from typing import Dict, Optional
import logging

from pushbullet import Pushbullet, PushbulletError, PushError  # type: ignore

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
    ValidationError,
    site,
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
        file_name: str = 'Snapshot.jpg',
        file_type: str = 'image/jpeg',
        file_content: Optional[bytes] = None,
    ) -> None:
        pb = Pushbullet(access_token)
        file_data = {'file_url': file_url, 'file_name': file_name, 'file_type': file_type}
        if file_content:
            try:
                file_data = pb.upload_file(file_content, file_name)
            except (PushError, PushbulletError):
                LOGGER.exception('could not upload to pushbullet')

        if file_url:
            pb.push_file(**file_data, body=body, title=title)
        else:
            pb.push_link(title, link, body)

    def send_failure_alert(self, context: FailureAlertContext, **kwargs) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        link = site.build_full_url('/')
        title = self.get_failure_alert_title(context=context, link=link)
        text = self.get_failure_alert_text(context=context, link=link)
        if not title or not text:
            return

        file_content = context.print.get_poster_url_content() if not context.site_is_public else None
        self.call_pushbullet(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            file_url=context.print.poster_url,
            file_name='Detected Failure.jpg',
            file_content=file_content,
        )

    def send_printer_notification(self, context: PrinterNotificationContext, **kwargs) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        title = self.get_printer_notification_title(context=context)
        text = self.get_printer_notification_text(context=context)
        if not text or not title:
            return

        file_content = context.print.get_poster_url_content() if not context.site_is_public else None
        link = site.build_full_url('/')

        self.call_pushbullet(
            access_token=access_token,
            title=title,
            body=text,
            link=link,
            file_url=context.print.poster_url,
            file_name='Snapshot.jpg',
            file_content=file_content,
        )

    def send_test_message(self, context: TestMessageContext, **kwargs) -> None:
        access_token = self.get_access_token_from_config(context.config)
        link = site.build_full_url('/')
        self.call_pushbullet(
            access_token=access_token,
            title='Test Notification',
            body='It works',
            link=link,
            file_url='',
        )


def __load_plugin__():
    return PushBulletNotificationPlugin()
