from typing import Dict, Optional, Any
import logging
import requests  # type: ignore
import io
from enum import IntEnum

from django.conf import settings

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
    ValidationError,
    site,
)

LOGGER = logging.getLogger(__name__)


class PushoverException(Exception):
    pass


class PushoverPriority(IntEnum):
    # See https://pushover.net/api#priority for more details on pushover notification priority
    LOWEST = -2  # Don't show any notification
    LOW = -1  # Show a quiet (non-alerting) notification
    NORMAL = 0  # Show a normal notification that respects a user's quiet hours
    HIGH = 1  # Show a high-priority notification that bypasses a user's quiet hours
    EMERGENCY = 2  # Show a high-priority notification that requires user confirmation


class PushOverNotificationPlugin(BaseNotificationPlugin):

    def validate_config(self, data: Dict) -> Dict:
        if 'user_key' in data:
            user_key = data['user_key'].strip()
            return {'user_key': user_key}
        raise ValidationError('user_key is missing from config')

    def get_user_key_from_config(self, config: Dict) -> str:
        if config and 'user_key' in config:
            return config['user_key']
        return ''

    def i(self, s: str) -> str:
        return f"<i>{s}</i>"

    def b(self, s: str):
        return f"<b>{s}</b>"

    def u(self, s: str):
        return f"<u>{s}</u>"

    def call_pushover(
        self,
        token: str,
        user_key: str,
        title: str,
        message: str,
        priority: Optional[PushoverPriority] = None,
        file_content: Optional[bytes] = None,
        timeout: float = 5.0,
    ) -> None:

        API_URL = "https://api.pushover.net/1/messages.json"
        RETRY = 60  # seconds
        EXPIRE = 120  # seconds

        if len(message) > 1024:
            raise PushoverException("Maximum message size of 1024 characters exceeded!")

        if title and len(title) > 250:
            raise PushoverException("Maximum title size of 250 characters exceeded!")

        payload: Dict[str, Any] = {
            "token": token,
            "user": user_key,
            "message": message,
            "html": 1,
        }

        if title:
            payload["title"] = title

        if priority:
            payload["priority"] = int(priority)

            if priority == PushoverPriority.EMERGENCY:
                # retry every RETRY seconds for EXPIRE seconds total
                payload["retry"] = RETRY
                payload["expire"] = EXPIRE

        files = None
        if file_content:
            files = {
                "attachment": io.BytesIO(file_content)
            }

        req = requests.post(API_URL, data=payload, files=files, timeout=timeout)
        req.raise_for_status()

    def send_failure_alert(self, context: FailureAlertContext, **kwargs) -> None:
        if not settings.PUSHOVER_APP_TOKEN:
            return

        user_key = self.get_user_key_from_config(context.config)
        if not user_key:
            return

        link = site.build_full_url('/')
        title = self.get_failure_alert_title(context=context, link=link)
        text = self.get_failure_alert_text(context=context, link=link)
        if not title or not text:
            return

        file_content = context.print.get_poster_url_content() if not context.site_is_public else None
        self.call_pushover(
            token=settings.PUSHOVER_APP_TOKEN,
            user_key=user_key,
            priority=PushoverPriority.HIGH,
            title=title,
            message=text,
            file_content=file_content,
        )

    def send_printer_notification(self, context: PrinterNotificationContext, **kwargs) -> None:
        if not settings.PUSHOVER_APP_TOKEN:
            return

        user_key = self.get_user_key_from_config(context.config)
        if not user_key:
            return

        title = self.get_printer_notification_title(context=context)
        text = self.get_printer_notification_text(context=context)
        if not title or not text:
            return

        file_content = context.print.get_poster_url_content()
        self.call_pushover(
            token=settings.PUSHOVER_APP_TOKEN,
            user_key=user_key,
            title=title,
            message=text,
            file_content=file_content,
        )

    def send_test_message(self, context: TestMessageContext, **kwargs) -> None:
        user_key = self.get_user_key_from_config(context.config)
        self.call_pushover(
            token=settings.PUSHOVER_APP_TOKEN or '',
            user_key=user_key,
            title='Test Notification',
            message='It works!',
        )


def __load_plugin__():
    return PushOverNotificationPlugin()
