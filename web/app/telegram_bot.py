from telebot import TeleBot, types
from django.conf import settings
from lib import site
from .models import Printer

import logging

LOGGER = logging.getLogger(__name__)

def telegram_bot():
    bot = None

    if settings.TELEGRAM_BOT_TOKEN:
        bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)

    return bot

bot_name = None
bot = telegram_bot()
if bot:
    bot_name = bot.get_me().username

def default_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('Go to The Spaghetti Detective to take a closer look.',
        url=site.build_full_url('/printers/')))
    return markup

def inline_markup(printer, buttons=['more_info']):
    links = {
        'cancel': { 'text': 'Yes it failed. Cancel the print!', 'url': site.build_full_url('/printers/{}/cancel/'.format(printer.id)) },
        'resume': { 'text': 'It is a false alarm. Resume the print!', 'url': site.build_full_url('/printers/{}/resume/'.format(printer.id)) },
        'do_not_ask': { 'text': 'Resume the print, and don\'t alert me for the rest of this print.', 'url': site.build_full_url('/printers/{}/resume/?mute_alert=true'.format(printer.id)) },
        'more_info': { 'text': 'Go to The Spaghetti Detective to take a closer look.', 'url': site.build_full_url('/printers/') }
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

    if photo:
        bot.send_photo(chat_id, photo, caption=notification, parse_mode='Markdown', reply_markup=keyboard)
    else:
        bot.send_message(chat_id, notification, parse_mode='Markdown', reply_markup=keyboard)
