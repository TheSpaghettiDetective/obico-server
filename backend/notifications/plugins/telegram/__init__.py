from typing import Dict, Optional, List
import logging
import os
import time
from telebot import TeleBot, types  # type: ignore
from django.conf import settings
import requests
from rest_framework.serializers import ValidationError

from lib import syndicate

from notifications.plugin import (
    BaseNotificationPlugin,
    PrinterNotificationContext,
    FailureAlertContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class TelegramNotificationPlugin(BaseNotificationPlugin):

    def i(self, s: str) -> str:
        return f"<i>{s}</i>"

    def b(self, s: str) -> str:
        return f"<b>{s}</b>"

    def a(self, s: str) -> str:
        return f'<a href="{s}">{s}</a>'

    def env_vars(self) -> Dict:
        bot_name = None
        bot = self.get_telegram_bot()
        try:
            bot_name = bot.get_me().username
        except Exception as e:
            LOGGER.warn("Couldn't get telegram bot name: " + str(e))

        return {
            'TELEGRAM_BOT_TOKEN': {
                'is_required': True,
                'is_set': 'TELEGRAM_BOT_TOKEN' in os.environ,
            },
            'TELEGRAM_BOT_NAME': {
                'is_required': False,
                'value': bot_name
            },
        }

    def validate_config(self, data: Dict) -> Dict:
        if 'chat_id' in data:
            chat_id = data['chat_id'].strip()
            return {'chat_id': chat_id}
        raise ValidationError('chat_id is missing from config')

    def get_chat_id_from_config(self, config: Dict) -> str:
        if config and 'chat_id' in config:
            return config['chat_id']
        return ''

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        chat_id = self.get_chat_id_from_config(context.config)
        if not chat_id:
            return

        link = syndicate.build_full_url_for_syndicate('/printers/', context.user.syndicate_name)
        text = self.get_failure_alert_text(context=context, link=link)
        if not text:
            return

        buttons = ['more_info']
        if context.print_paused:
            buttons = ['cancel', 'resume', 'do_not_ask', 'more_info']
        elif context.printer.pause_on_failure and context.is_warning:
            buttons = ['cancel', 'more_info']

        message = f"Hi {context.user.first_name},\n{text}"

        try:
            file_content = requests.get(context.img_url).content
        except:
            file_content = None

        markups = self.inline_buttons(context, buttons) if file_content else self.default_button()

        self.call_telegram(
            chat_id=chat_id,
            message=message,
            markups=markups,
            file_content=file_content,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        chat_id = self.get_chat_id_from_config(context.config)
        if not chat_id:
            return

        text = self.get_printer_notification_text(context=context)
        if not text:
            return

        message = f"Hi {context.user.first_name},\n{text}"

        try:
            file_content = requests.get(context.img_url).content
        except:
            file_content = None

        self.call_telegram(
            chat_id=chat_id,
            message=message,
            file_content=file_content,
        )

    def send_test_message(self, context: TestMessageContext) -> None:
        chat_id = self.get_chat_id_from_config(context.config)
        self.call_telegram(
            chat_id=chat_id,
            message='It works!',
        )

    def call_telegram(
        self,
        chat_id: str,
        message: str,
        markups: Optional[List] = None,
        file_content: Optional[bytes] = None,
    ) -> None:
        bot = self.get_telegram_bot()
        if not bot:
            return

        attempts = 0

        while attempts < 2:
            try:
                if file_content:
                    self._send(
                        bot.send_photo,
                        chat_id,
                        file_content,
                        caption=message,
                        parse_mode='HTML',
                        reply_markup=markups)
                else:
                    self._send(
                        bot.send_message,
                        chat_id,
                        message,
                        parse_mode='HTML',
                        reply_markup=markups)
                return
            except ConnectionError:
                attempts += 1
                time.sleep(0.05)

    def _send(self, bot_method, *args, **kwargs):
        attempts = 0
        while attempts < 2:
            try:
                return bot_method(*args, **kwargs)
            except ConnectionError:
                attempts += 1
                time.sleep(0.05)

    def default_button(self):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(
            'Go to the Obico app to take a closer look.',
            url=syndicate.build_full_url_for_syndicate('/printers/', context.user.syndicate_name))
        )
        return markup

    def inline_buttons(self, context: FailureAlertContext, buttons=['more_info']):
        print_id = context.print.id
        links = {
            'cancel': {
                'text': 'Yes it failed. Cancel the print!',
                'url': syndicate.build_full_url_for_syndicate(f'/prints/{print_id}/cancel/', context.user.syndicate_name)
            },
            'resume': {
                'text': 'It is a false alarm. Resume the print!',
                'url': syndicate.build_full_url_for_syndicate(f'/prints/{print_id}/resume/', context.user.syndicate_name)
            },
            'do_not_ask': {
                'text': 'Resume the print, and don\'t alert me for the rest of this print.',
                'url': syndicate.build_full_url_for_syndicate(f'/prints/{print_id}/resume/?mute_alert=true', context.user.syndicate_name)
            },
            'more_info': {
                'text': 'Go to the Obico app to take a closer look.',
                'url': syndicate.build_full_url_for_syndicate('/printers/', context.user.syndicate_name)
            }
        }

        button_list = [
            types.InlineKeyboardButton(links[button]['text'], url=links[button]['url'])
            for button in buttons
        ]
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*button_list)
        return markup

    def get_telegram_bot(self):
        bot = None
        if os.environ.get('TELEGRAM_BOT_TOKEN'):
            bot = TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
        return bot


def __load_plugin__():
    return TelegramNotificationPlugin()
