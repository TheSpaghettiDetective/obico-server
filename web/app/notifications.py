from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings
import requests
import logging

from lib import site

LOGGER = logging.getLogger(__name__)

def send_failure_alert(printer, pause_print):
    send_failure_alert_sms(printer, pause_print)
    send_failure_alert_email(printer, pause_print)

def send_failure_alert_email(printer, pause_print):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
    try:
        from urllib.parse import urlparse
        import ipaddress
        if ipaddress.ip_address(urlparse(printer.pic['img_url']).hostname).is_global:
            attachments = []
        else:
            attachments = [('possible_failure.jpg', requests.get(printer.pic['img_url']).content, 'image/jpeg')]
    except:
        attachments = []

    subject = 'Your print {} may be failing on {}'.format(printer.current_print.filename or '', printer.name)
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'printer': printer,
        'pause_print': pause_print,
        'view_link': site.build_full_url('/printers/'),
        'cancel_link': site.build_full_url('/printers/{}/cancel/'.format(printer.id)),
        'resume_link': site.build_full_url('/printers/{}/resume/?mute_alert=true'.format(printer.id)),
        'insert_img': len(attachments) == 0,
    }

    message = get_template('email/failure_alert.html').render(ctx)
    msg = EmailMessage(subject, message, to=(printer.user.email,), from_email=from_email, attachments=attachments)
    msg.content_subtype = 'html'
    msg.send()

def send_failure_alert_sms(printer, pause_print):
    if not settings.TWILIO_ENABLED:
        LOGGER.warn("Twilio settings are missing. Ignored send requests")
        return

    if not printer.user.sms_eligible():
        return

    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    from_number = settings.TWILIO_FROM_NUMBER

    to_number = printer.user.phone_country_code + printer.user.phone_number
    msg = 'The Spaghetti Detective - Your print {} may be failing on {}. {}Go check it at: {}'.format(
        printer.current_print.filename or '',
        printer.name,
        'Printer is paused. ' if pause_print else '',
        site.build_full_url('/'))
    twilio_client.messages.create(body=msg, to=to_number, from_=from_number)
