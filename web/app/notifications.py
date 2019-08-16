from allauth.account.admin import EmailAddress
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings
from pushbullet import Pushbullet, PushbulletError, PushError
from telebot import TeleBot, types
import requests
import logging
from urllib.parse import urlparse
import ipaddress

from app.models import Printer
import app.telegram_bot
from lib import site

LOGGER = logging.getLogger(__name__)
TELEGRAM_BOT = TeleBot(settings.TELEGRAM_BOT_TOKEN)

def notification_elements(printer, is_warning, print_paused):
    title = 'The Spaghetti Detective - Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')

    pausing_msg = ''
    if print_paused:
        pausing_msg = 'Printer is paused.'
    elif printer.action_on_failure == Printer.PAUSE and is_warning:
        pausing_msg = 'Printer is NOT paused because The Detective is not very sure about it.'


    link = site.build_full_url('/')

    body = '{}\nGo check it at: {}'.format(pausing_msg, link)

    return { 'title': title, 'body': body, 'link': link }

def get_photo(printer):
    try:
        if ipaddress.ip_address(urlparse(printer.pic['img_url']).hostname).is_global:
            return None
        else:
            return requests.get(printer.pic['img_url']).content
    except:
        return None

def send_failure_alert(printer, is_warning=True, print_paused=False):
    send_failure_alert_sms(printer, is_warning, print_paused)
    send_failure_alert_email(printer, is_warning, print_paused)
    send_failure_alert_pushbullet(printer, is_warning, print_paused)
    send_failure_alert_telegram(printer, is_warning, print_paused)

def send_failure_alert_email(printer, is_warning, print_paused):
    if not settings.EMAIL_HOST:
        LOGGER.warn('Email settings are missing. Ignored send requests')
        return

    # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
    photo = get_photo(printer)
    attachments = []
    if photo:
        attachments = [('Detected Failure.jpg', photo, 'image/jpeg')]

    subject = 'Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'printer': printer,
        'print_paused': print_paused,
        'is_warning': is_warning,
        'view_link': site.build_full_url('/printers/'),
        'cancel_link': site.build_full_url('/printers/{}/cancel/'.format(printer.id)),
        'resume_link': site.build_full_url('/printers/{}/resume/?mute_alert=true'.format(printer.id)),
        'insert_img': len(attachments) == 0,
    }

    # By default email verification should be required for notifications but
    # maybe users will want to disable it on private servers
    if settings.ACCOUNT_EMAIL_VERIFICATION != 'none':
        emails = EmailAddress.objects.filter(user=printer.user, verified=True)
    else:
        emails = EmailAddress.objects.filter(user=printer.user)
    message = get_template('email/failure_alert.html').render(ctx)
    for email in emails:
        msg = EmailMessage(subject, message, to=(email.email,), from_email=from_email, attachments=attachments)
        msg.content_subtype = 'html'
        msg.send()

def send_failure_alert_sms(printer, is_warning, print_paused):
    if not settings.TWILIO_ENABLED:
        LOGGER.warn('Twilio settings are missing. Ignored send requests')
        return

    if not printer.user.sms_eligible():
        return

    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    from_number = settings.TWILIO_FROM_NUMBER

    to_number = printer.user.phone_country_code + printer.user.phone_number
    notification_text = notification_elements(printer, is_warning, print_paused)

    msg = '{}. {}'.format(notification_text['title'], notification_text['body'])
    twilio_client.messages.create(body=msg, to=to_number, from_=from_number)


def send_failure_alert_pushbullet(printer, is_warning, print_paused):
    if not printer.user.has_valid_pushbullet_token():
        return

    pb = Pushbullet(printer.user.pushbullet_access_token)
    notification_text = notification_elements(printer, is_warning, print_paused)
    title, link, body = notification_text['title'], notification_text['link'], notification_text['body']

    try:
        file_url = None
        try:
            file_url = printer.pic['img_url']
            if not ipaddress.ip_address(urlparse(file_url).hostname).is_global:
                pb.upload_file(requests.get(file_url).content, 'Detected Failure.jpg')
        except:
            pass

        if file_url:
            pb.push_file(file_url=file_url, file_name='Detected Failure.jpg', file_type='image/jpeg', body=body, title=title)
        else:
            pb.push_link(title, link, body)
    except PushError as e:
        LOGGER.error(e)
    except PushbulletError as e:
        LOGGER.error(e)

def send_failure_alert_telegram(printer, is_warning, print_paused):
    if not printer.user.telegram_eligible():
        return

    chat_id = printer.user.telegram_chat_id
    notification_text = notification_elements(printer, is_warning, print_paused)

    photo = get_photo(printer)

    telegram_bot.send_notification(chat_id, notification_text, photo, printer_id)
