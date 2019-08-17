from telebot import TeleBot, types
from django.conf import settings
from django.urls import reverse
from lib import site
from lib.redis import REDIS
from secrets import token_hex
from ipaddress import ip_address, ip_network
from .models import User, Printer

import logging

LOGGER = logging.getLogger(__name__)
bot = None
bot_name = None

if settings.TELEGRAM_BOT_TOKEN:
    try:
        bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
        bot_name = bot.get_me().username
    except:
        bot, bot_name = None, None

# This list from https://core.telegram.org/bots/webhooks
TELEGRAM_CALLBACK_IPS = [ip_network('149.154.160.0/20'), ip_network('91.108.4.0/22')]

def valid_telegram_ip(ip):
    return any([ip in network for network in TELEGRAM_CALLBACK_IPS])

def webhooks_enabled():
    try:
        return not not bot.get_webhook_info().url # coerce string into bool
    except:
        return False

# A middleware for enabling webhooks for telegram. Webhooks require https to be set up.
def enable_webhooks(get_response):
    def middleware(request):
        # Try/except in case a user is running the bot locally
        # and doesn't have a web-accessible url
        try:
            if not webhooks_enabled():
                bot.set_webhook( site.build_full_url(reverse('telegram'), request) )
        except Exception as e:
            LOGGER.warning(e)

        return get_response(request)

    return middleware

# When the bot sends a notification, we stick a secret key into redis with their userid as a value.
# We use this to securely connect the callback to their uuid.
# See https://core.telegram.org/bots#deep-linking-example for more info.
def generate_callback_secret(user):
    secret = token_hex(12)
    REDIS.set(secret, user.id, nx=True)
    return secret

def closer_look_button():
    return types.InlineKeyboardButton('Go to The Spaghetti Detective to take a closer look.', url=site.build_full_url('/printers/'))

def default_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(closer_look_button())
    return markup

def inline_markup(printer):
    secret = generate_callback_secret(printer.user)
    callback_data = lambda callback: f'{callback}|{printer.id}|{secret}'

    if webhooks_enabled():
        button_list = [
            types.InlineKeyboardButton('Yes it failed. Cancel the print!',
                callback_data=callback_data('print_failed')),
            types.InlineKeyboardButton('It is a false alarm. Resume the print!',
                callback_data=callback_data('resume')),
            types.InlineKeyboardButton("Resume the print, and don't alert me for the rest of this print.",
                callback_data=callback_data('do_not_ask')),
            closer_look_button()
        ]
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*button_list)
    else:
        markup = default_markup()

    return markup

def notification_text():
    # The telegram bot will send a message based on the failure_alert.html template,
    # rather than the pushbullet/sms template.
    return """Hi {},

The Spaghetti Detective spotted some suspicious activity on your printer {}.

{}"""

def initialize_response_objects(chat_id, action, printer):
    notification = notification_text().format(
        printer.user.first_name or '',
        printer.name,
        action)
    return [notification, inline_markup(printer)]

def confirm_print_failed(chat_id, message_id, printer):
    if not bot:
        return

    secret = generate_callback_secret(printer.user)
    callback_data = lambda callback: f'{callback}|{printer.id}|{secret}'

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
    user_id = REDIS.get(secret)
    REDIS.delete(secret)

    return User.objects.get(pk=user_id)

def get_printer(user, printer_id):
    return Printer.objects.filter(user=user).get(pk=printer_id)

def reset_markup(chat_id, message_id):
    return bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=default_markup()
    )

def send_notification(printer, action, photo):
    if not bot:
        return

    chat_id = printer.user.telegram_chat_id
    telegram_user = bot.get_chat(chat_id)
    notification, keyboard = initialize_response_objects(telegram_user, action, printer)

    if photo:
        bot.send_photo(chat_id, photo, caption=notification, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, notification, reply_markup=default_markup())

def handle_callback_query(call):
    if not bot:
        return False

    command, printer_id, secret = call['data'].split('|')
    chat_id, message_id = call['message']['chat']['id'], call['message']['message_id']

    reply = ''
    succeeded = False

    try:
        user = get_user(secret)
        printer = get_printer(user, printer_id)

        if command == 'nevermind':
            return bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=inline_markup(printer))
        elif command == 'print_failed':
            return confirm_print_failed(chat_id, message_id, printer)

        if command == 'resume':
            succeeded, alert_acknowledged = printer.resume_print()
            reply = 'Resumed the print' if succeeded else 'Could not resume the print'
        elif command == 'do_not_ask':
            succeeded, alert_acknowledged = printer.resume_print(mute_alert=True)
            reply = 'Resumed the print. Will not pause again during this print' if succeeded else 'Could not resume the print'
        elif command == 'cancel':
            succeeded, alert_acknowledged = printer.cancel_print()
            reply = 'Canceled the print' if succeeded else 'Could not cancel the print'

        bot.answer_callback_query(call['id'], reply)

        action = f'✅ {reply}' if succeeded else f'❌ {reply}'
        notification, _ = initialize_response_objects(chat_id, action, printer)

        bot.edit_message_caption(notification, chat_id=chat_id, message_id=message_id)
    except:
        pass

    reset_markup(chat_id, message_id)
    return succeeded
