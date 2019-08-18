from telebot import TeleBot, types
from django.conf import settings
from lib import site
from .models import Printer

import logging

LOGGER = logging.getLogger(__name__)
bot = None
bot_name = None
webhooks_enabled = True

if settings.TELEGRAM_BOT_TOKEN:
    try:
        bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
        bot_name = bot.get_me().username
    except:
        bot, bot_name = None, None

MORE_INFO_LINK = site.build_full_url('/printers/')

def default_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('Go to The Spaghetti Detective to take a closer look.',
        url=MORE_INFO_LINK))
    return markup

def inline_markup(printer):
    links = {
        'cancel': site.build_full_url('/printers/{}/cancel/'.format(printer.id)),
        'resume': site.build_full_url('/printers/{}/resume/'.format(printer.id)),
        'do_not_ask': site.build_full_url('/printers/{}/resume/?mute_alert=true'.format(printer.id)),
        'more_info': MORE_INFO_LINK
    }

    button_list = [
        types.InlineKeyboardButton('Yes it failed. Cancel the print!',
            url=links['cancel']),
        types.InlineKeyboardButton('It is a false alarm. Resume the print!',
            url=links['resume']),
        types.InlineKeyboardButton("Resume the print, and don't alert me for the rest of this print.",
            url=links['do_not_ask']),
        types.InlineKeyboardButton('Go to The Spaghetti Detective to take a closer look.',
            url=links['more_info'])
    ]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*button_list)

    return markup

def send_notification(printer, notification, photo):
    if not bot:
        return

    chat_id = printer.user.telegram_chat_id
    telegram_user = bot.get_chat(chat_id)
    keyboard = default_markup() if not photo else inline_markup(printer)

    if photo:
        bot.send_photo(chat_id, photo, caption=notification, parse_mode='Markdown', reply_markup=keyboard)
    else:
        bot.send_message(chat_id, notification, parse_mode='Markdown', reply_markup=keyboard)
