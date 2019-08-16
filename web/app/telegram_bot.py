from telebot import TeleBot, types
from django.conf import settings
from lib import site
import logging
import sys

from .models import User, Printer

LOGGER = logging.getLogger(__name__)

bot = None
bot_name = None
webhooks_enabled = False

if settings.TELEGRAM_BOT_TOKEN:
    try:
        bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
        bot_name = bot.get_me().username
    except:
        bot, bot_name = None, None

    # This is in case a user is running the bot locally and doesn't have a web-accessible url
    try:
        bot.set_webhook(site.build_full_url('/telegram/'))
        webhooks_enabled = True
    except:
        webhooks_enabled = False

def closer_look_button():
    return types.InlineKeyboardButton('Go to The Spaghetti Detective to take a closer look.', url=site.build_full_url('/printers/'))

def inline_markup(user, printer_id=None):
    secret = user.telegram_secret
    callback_data = lambda callback: f'{callback}|{printer_id}|{secret}'

    if webhooks_enabled:
        button_list = [
            types.InlineKeyboardButton('Yes it failed. Cancel the print!',
                callback_data=callback_data('print_failed')),
            types.InlineKeyboardButton('It is a false alarm. Resume the print!',
                callback_data=callback_data('resume')),
            types.InlineKeyboardButton("Resume the print, and don't alert me for the rest of this print.",
                callback_data=callback_data('do_not_ask')),
            closer_look_button()
        ]
    else:
        button_list = [closer_look_button()]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*button_list)
    return markup

def initialize_response_objects(chat_id, notification_text, user, printer_id=None):
    notification = '{}. {}'.format(notification_text['title'], notification_text['body'])
    return [notification, inline_markup(user, printer_id)]

def confirm_print_failed(chat_id, message_id, secret, printer_id=None):
    if not bot:
        return

    callback_data = lambda callback: f'{callback}|{printer_id}|{secret}'

    button_list_confirm = [
        types.InlineKeyboardButton("I'm sure it failed. Cancel the print.",
            callback_data=callback_data('cancel')),
        types.InlineKeyboardButton("I changed my mind. Don't cancel the print.",
            callback_data=callback_data('nevermind'))
    ]

    markup_confirm = types.InlineKeyboardMarkup(row_width=1)
    markup_confirm.add(*button_list_confirm)

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup_confirm)

def get_user(secret):
    users = User.objects.filter(telegram_secret=secret)

    if len(users) is not 1:
        LOGGER.warning('Callback called with invalid secret.')
        raise

    return users[0]

def get_printer(user, printer_id):
    printer = Printer.objects.filter(user=user, id=printer_id)

    if len(printers) is not 1:
        LOGGER.warning('Callback called with invalid printer id.')
        raise

    return printers[0]

def reset_markup(chat_id, message_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(closer_look_button())
    return bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)

def send_notification(chat_id, notification_text, photo, user, printer_id=None):
    if not bot:
        return

    telegram_user = bot.get_chat(chat_id)
    notification, keyboard = initialize_response_objects(telegram_user, notification_text, user, printer_id=None)

    if photo:
        bot.send_photo(chat_id, photo, caption=notification, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, notification)

def handle_callback_query(call):
    if not bot:
        return

    command, printer_id, secret = call['data'].split('|')
    chat_id, message_id = call['message']['chat']['id'], call['message']['message_id']

    try:
        user = get_user(secret)
    except:
        reset_markup(chat_id, message_id)
        return False

    if command == 'nevermind':
        return bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=inline_markup(user, printer_id))
    elif command == 'print_failed':
        return confirm_print_failed(chat_id, message_id, secret, printer_id)

    try:
        printer = get_printer(printer_id)
    except:
        reset_markup(chat_id, message_id)
        return False

    reply = ''
    succeeded = False
    if command == 'resume':
        succeeded, alert_acknowledged = printer.resume_print()
        reply = 'Resumed the print' if succeeded else 'Could not resume the print'
    elif command == 'do_not_ask':
        succeeded, alert_acknowledged = printer.resume_print(mute_alert=True)
        reply = 'Resumed the print. Will not pause again during this print' if succeeded else 'Could not resume the print'
    elif command == 'cancel':
        succeeded, alert_acknowledged = printer.cancel_print()
        reply = 'Canceled the print' if succeeded else 'Could not cancel the print'

    prefix = "✅" if succeeded else "❌"
    bot.answer_callback_query(call['id'], reply)
    bot.edit_message_caption(f'{prefix} {reply}', chat_id=chat_id, message_id=message_id)
    reset_markup(chat_id, message_id)

    return succeeded
