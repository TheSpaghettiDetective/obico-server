from telebot import TeleBot, types
from django.conf import settings
from lib import site
import os
from app.models import Printer
import time

import logging

LOGGER = logging.getLogger(__name__)

def telegram_bot():
    bot = None

    if os.environ.get('TELEGRAM_BOT_TOKEN'):
        bot = TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))

    return bot

bot_name = None
bot = telegram_bot()
if bot:
    try:
        bot_name = bot.get_me().username
    except Exception as e:
        LOGGER.warn("Couldn't get telegram bot name: " + str(e))

def default_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('Go to the Obico app to take a closer look.',
        url=site.build_full_url('/printers/')))
    return markup

def inline_markup(printer, buttons=['more_info']):
    links = {
        'cancel': { 'text': 'Yes it failed. Cancel the print!', 'url': site.build_full_url('/prints/{}/cancel/'.format(printer.current_print_id)) },
        'resume': { 'text': 'It is a false alarm. Resume the print!', 'url': site.build_full_url('/prints/{}/resume/'.format(printer.current_print_id)) },
        'do_not_ask': { 'text': 'Resume the print, and don\'t alert me for the rest of this print.', 'url': site.build_full_url('/prints/{}/resume/?mute_alert=true'.format(printer.current_print_id)) },
        'more_info': { 'text': 'Go to the Obico app to take a closer look.', 'url': site.build_full_url('/printers/') }
    }

    button_list = [
        types.InlineKeyboardButton(links[button]['text'], url=links[button]['url']) for button in buttons
    ]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*button_list)

    return markup


def send_notification(printer, notification, photo, buttons=None):
    bot = telegram_bot()
    if not bot:
        return

    chat_id = printer.user.telegram_chat_id

    keyboard = None

    if buttons:
        keyboard = inline_markup(printer, buttons) if photo else default_markup()

    attempts = 0

    while attempts < 2:
        try:
            if photo:
                telegram_send(
                    bot.send_photo,
                    chat_id,
                    photo,
                    caption=notification,
                    parse_mode='Markdown',
                    reply_markup=keyboard)
            else:
                telegram_send(
                    bot.send_message,
                    chat_id,
                    notification,
                    parse_mode='Markdown',
                    reply_markup=keyboard)
            return
        except ConnectionError:
            attempts += 1
            time.sleep(0.05)


def telegram_send(bot_method, *args, **kwargs):
    attempts = 0
    while attempts < 2:
        try:
            return bot_method(*args, **kwargs)
        except ConnectionError:
            attempts += 1
            time.sleep(0.05)
