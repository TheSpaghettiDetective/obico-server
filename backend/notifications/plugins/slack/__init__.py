from typing import Dict, Optional
import logging
import requests  # type: ignore
import os
from rest_framework.serializers import ValidationError

from lib import site as site

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class SlackNotificationPlugin(BaseNotificationPlugin):

    def env_vars(self) -> Dict:
        return {
            'SLACK_CLIENT_ID': {
                'is_required': True,
                'is_set': 'SLACK_CLIENT_ID' in os.environ,
                'value': os.environ.get('SLACK_CLIENT_ID'),
            },
            'SLACK_CLIENT_SECRET': {
                'is_required': True,
                'is_set': 'SLACK_CLIENT_SECRET' in os.environ,
            },
        }

    def validate_config(self, data: Dict) -> Dict:
        if 'access_token' in data:
            access_token = data['access_token'].strip()
            return {'access_token': access_token}
        raise ValidationError('access_token is missing from config')

    def get_access_token_from_config(self, config: Dict) -> str:
        if config and 'access_token' in config:
            return config['access_token']
        return ''

    def i(self, s: str) -> str:
        return f"_{s}_"

    def b(self, s: str) -> str:
        return f"*{s}*"

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        title = self.get_failure_alert_text(context=context)
        text = self.get_failure_alert_text(context=context)
        if not title or not text:
            return

        text += f"\n<{site.build_full_url('/printers/')}|Check it out.>"

        self.call_slack(
            access_token=access_token,
            text=text,
            image_url=context.img_url,
        )

    def call_slack(self, access_token: str, text: str, image_url: Optional[str] = None, timeout: float = 5.0) -> None:
        req = requests.get(
            url='https://slack.com/api/conversations.list',
            params={
                'types': 'public_channel,private_channel'
            },
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=timeout,
        )
        req.raise_for_status()
        slack_channel_ids = [c['id'] for c in req.json()['channels'] if c['is_member']]

        for slack_channel_id in slack_channel_ids:
            msg = {
                "channel": slack_channel_id,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": text,
                        }
                    }
                ]
            }
            msg['blocks'].append(
                {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "Print snapshot"
                }
            )

            req = requests.post(
                url='https://slack.com/api/chat.postMessage',
                headers={'Authorization': f'Bearer {access_token}'},
                json=msg,
                timeout=timeout,
            )
            req.raise_for_status()

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        if not access_token:
            return

        title = self.get_printer_notification_title(context=context)
        text = self.get_printer_notification_text(context=context)
        if not title or not text:
            return

        self.call_slack(
            access_token=access_token,
            text=text,
            image_url=context.img_url,
        )

    def send_test_message(self, context: TestMessageContext) -> None:
        access_token = self.get_access_token_from_config(context.config)
        self.call_slack(
            access_token=access_token,
            text='TSD Test Notification - It works!',
        )


def __load_plugin__():
    return SlackNotificationPlugin()
