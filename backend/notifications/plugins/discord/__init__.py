from typing import Dict, Optional
import logging
from django.conf import settings
from rest_framework.serializers import ValidationError

from discord_webhook import DiscordWebhook, DiscordEmbed  # type: ignore
from lib import syndicate
from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext, PrinterNotificationContext, TestMessageContext,
    notification_types,
)

LOGGER = logging.getLogger(__name__)


class DiscordNotificationPlugin(BaseNotificationPlugin):
    FAILURE_COLOR = 0xcf142b  # stop red
    HAZZARD_COLOR = 0xEED202  # hazard yellow
    INFO_COLOR = 0x9863F4  # purple, as used on the main website
    OK_COLOR = 0x33a532

    def validate_config(self, data: Dict) -> Dict:
        if 'webhook_url' in data:
            webhook_url = data['webhook_url'].strip()
            return {'webhook_url': webhook_url}
        raise ValidationError('webhook_url key is missing from config')

    def i(self, s: str) -> str:
        return "_{}_".format(s.replace('_', '\_'))

    def b(self, s: str) -> str:
        return "**{}**".format(s.replace('*', '\*'))

    def u(self, s: str) -> str:
        return "__{}__".format(s.replace('_', '\_'))

    @classmethod
    def call_webhook(self, syndicate_name, title: str, text: str, color: int, webhook_url: str, image_url: Optional[str] = None):
        webhook = DiscordWebhook(url=webhook_url, username="Obico")
        embed = DiscordEmbed(title=title, description=text, color=color)
        if image_url:
            embed.set_image(url=image_url)

        embed.set_author(
            name="Obico Printer Notification",
            url=syndicate.build_full_url_for_syndicate('/printers/', syndicate_name),
            icon_url="https://obico.io/img/favicon.png"
        )
        embed.set_timestamp()
        embed.set_footer(text="The Obico app")
        webhook.add_embed(embed)
        webhook.execute()

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        if 'webhook_url' not in context.config:
            return

        color = self.INFO_COLOR

        if context.is_warning and context.print_paused:
            color = self.FAILURE_COLOR
        elif context.is_warning:
            color = self.HAZZARD_COLOR

        text = self.get_failure_alert_text(context=context)
        if not text:
            return

        text = f"Hi {context.user.first_name or ''},\n{text}"

        self.call_webhook(
            context.user.syndicate_name,
            title=context.printer.name,
            text=text,
            color=color,
            webhook_url=context.config['webhook_url'],
            image_url=context.img_url,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        if 'webhook_url' not in context.config:
            return

        color = self.notification_type_to_color(notification_type=context.notification_type)
        text = self.get_printer_notification_text(context=context)
        if not text:
            return

        text = f"Hi {context.user.first_name or ''},\n{text}"

        self.call_webhook(
            context.user.syndicate_name,
            title=context.printer.name,
            text=text,
            color=color,
            webhook_url=context.config['webhook_url'],
            image_url=context.img_url,
        )

    def notification_type_to_color(self, notification_type: str) -> int:
        if notification_type in (notification_types.PrintCancelled, ):
            return self.FAILURE_COLOR

        if notification_type in (notification_types.FilamentChange, ):
            return self.HAZZARD_COLOR

        if notification_type in (notification_types.PrintDone, ):
            return self.OK_COLOR

        return self.INFO_COLOR

    def send_test_message(self, context: TestMessageContext) -> None:
        self.call_webhook(
            context.user.syndicate_name,
            title='Test Notification',
            text='It works!',
            color=self.OK_COLOR,
            webhook_url=context.config.get('webhook_url', ''),
            image_url='',
        )


def __load_plugin__():
    return DiscordNotificationPlugin()
