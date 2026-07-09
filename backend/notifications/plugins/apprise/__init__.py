from typing import Dict, Optional
import logging

import apprise  # type: ignore
from rest_framework.serializers import ValidationError

from lib import syndicate

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class AppriseNotificationPlugin(BaseNotificationPlugin):
    """Send notifications through Apprise (https://github.com/caronc/apprise).

    Apprise turns a single URL into a notification to one of ~100 services
    (ntfy, Matrix, Gotify, Home Assistant, and many more). The user configures
    one Apprise URL and Obico forwards every enabled event to it, so we don't
    have to add code for each service one by one.
    """

    def validate_config(self, data: Dict) -> Dict:
        if 'apprise_url' not in data:
            raise ValidationError('apprise_url is missing from config')

        apprise_url = data['apprise_url'].strip()

        # Apprise.add() returns False when it can't parse the URL into a known
        # service. Reject it here so the user gets immediate feedback instead of
        # a silent no-op when a notification is later sent.
        if apprise_url and not apprise.Apprise().add(apprise_url):
            raise ValidationError('apprise_url is not a valid Apprise URL')

        return {'apprise_url': apprise_url}

    def get_apprise_url_from_config(self, config: Dict) -> str:
        if config and 'apprise_url' in config:
            return config['apprise_url']
        return ''

    def i(self, s: str) -> str:
        return f"<i>{s}</i>"

    def b(self, s: str) -> str:
        return f"<b>{s}</b>"

    def u(self, s: str) -> str:
        return f"<u>{s}</u>"

    def send_notification(
        self,
        apprise_url: str,
        title: str,
        body: str,
        img_url: Optional[str] = None,
    ) -> None:
        apobj = apprise.Apprise()
        if not apobj.add(apprise_url):
            LOGGER.warning('Ignoring notification: Apprise could not parse the configured URL')
            return

        # The title/body helpers on the base plugin emit <b>/<i>/<u> tags, so
        # tell Apprise to treat the body as HTML.
        apobj.notify(
            title=title,
            body=body,
            body_format=apprise.NotifyFormat.HTML,
            # Apprise fetches the image from this URL and forwards it as an
            # attachment to services that support attachments; others ignore it.
            attach=img_url or None,
        )

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        apprise_url = self.get_apprise_url_from_config(context.config)
        if not apprise_url:
            return

        link = syndicate.build_full_url_for_syndicate('/', context.user.syndicate_name)
        title = self.get_failure_alert_title(context=context, link=link)
        body = self.get_failure_alert_text(context=context, link=link)
        if not title or not body:
            return

        self.send_notification(
            apprise_url=apprise_url,
            title=title,
            body=body,
            img_url=context.img_url,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        apprise_url = self.get_apprise_url_from_config(context.config)
        if not apprise_url:
            return

        title = self.get_printer_notification_title(context=context)
        body = self.get_printer_notification_text(context=context)
        if not title or not body:
            return

        self.send_notification(
            apprise_url=apprise_url,
            title=title,
            body=body,
            img_url=context.img_url,
        )

    def send_test_message(self, context: TestMessageContext) -> None:
        apprise_url = self.get_apprise_url_from_config(context.config)
        if not apprise_url:
            return

        self.send_notification(
            apprise_url=apprise_url,
            title='Test Notification',
            body='It works!',
        )


def __load_plugin__():
    return AppriseNotificationPlugin()
