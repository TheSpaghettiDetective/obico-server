from allauth.account.admin import EmailAddress
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from twilio.rest import Client
from django.conf import settings
from pushbullet import Pushbullet, PushbulletError, PushError
import requests
import logging
from urllib.parse import urlparse
import ipaddress

from app.models import Printer, Print
from app.telegram_bot import send_notification as send_telegram_notification
from lib import site

LOGGER = logging.getLogger(__name__)

def send_failure_alert(printer, is_warning=True, print_paused=False):
    LOGGER.info(f'Sending alerts to {printer.user.id}')

    # Fixme: any exception will cause subsequent notification channel to be tried at all.
    # This is also why SMS is currently at the end, since it'll fail with exception when area code is not allowed.
    if printer.user.alert_by_email:
        send_failure_alert_email(printer, is_warning, print_paused)

    send_failure_alert_pushbullet(printer, is_warning, print_paused)
    send_failure_alert_telegram(printer, is_warning, print_paused)

    if printer.user.is_pro and printer.user.alert_by_sms:
        send_failure_alert_sms(printer, is_warning, print_paused)

def send_failure_alert_email(printer, is_warning, print_paused):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    subject = 'Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')

    ctx = {
        'printer': printer,
        'print_paused': print_paused,
        'is_warning': is_warning,
        'view_link': site.build_full_url('/printers/'),
        'cancel_link': site.build_full_url('/printers/{}/cancel/'.format(printer.id)),
        'resume_link': site.build_full_url('/printers/{}/resume/'.format(printer.id)),
    }

    unsub_url = site.build_full_url(f'/unsubscribe_email/?unsub_token={printer.user.unsub_token}&list=alert')
    send_email(
        printer.user,
        subject,
        unsub_url,
        'email/failure_alert.html',
        ctx,
        img_url=printer.pic['img_url'],
        )

def send_failure_alert_sms(printer, is_warning, print_paused):
    if not settings.TWILIO_ENABLED:
        LOGGER.warn("Twilio settings are missing. Ignored send requests")
        return

    if not printer.user.sms_eligible():
        return

    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    from_number = settings.TWILIO_FROM_NUMBER

    to_number = printer.user.phone_country_code + printer.user.phone_number

    pausing_msg = ''
    if print_paused:
        pausing_msg = 'Printer is paused. '
    elif printer.action_on_failure == Printer.PAUSE and is_warning:
        pausing_msg = 'Printer is NOT paused. '

    msg = 'The Spaghetti Detective - Your print {} on {} {}. {}Go check it at: {}'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing',
        pausing_msg,
        site.build_full_url('/'))
    twilio_client.messages.create(body=msg, to=to_number, from_=from_number)


def send_failure_alert_pushbullet(printer, is_warning, print_paused):
    if not printer.user.has_valid_pushbullet_token():
        return

    pausing_msg = ''
    if print_paused:
        pausing_msg = 'Printer is paused.'
    elif printer.action_on_failure == Printer.PAUSE and is_warning:
        pausing_msg = 'Printer is NOT paused because The Detective is not very sure about it.'

    pb = Pushbullet(printer.user.pushbullet_access_token)
    title = 'The Spaghetti Detective - Failure alert!'

    msg = 'Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')
    link = site.build_full_url('/')
    body = '{}\n{}\nGo check it at: {}'.format(msg, pausing_msg, link)

    try:
        file_url = None
        try:
            file_url = printer.pic['img_url']
            if not ipaddress.ip_address(urlparse(file_url).hostname).is_global:
                pb.upload_file(requests.get(file_url).content, 'Detected Failure.jpg')
        except:
            pass

        if file_url:
            pb.push_file(file_url=file_url, file_name="Detected Failure.jpg", file_type="image/jpeg", body=body, title=title)
        else:
            pb.push_link(title, link, body)
    except PushError as e:
        LOGGER.error(e)
    except PushbulletError as e:
        LOGGER.error(e)

def send_failure_alert_telegram(printer, is_warning, print_paused):
    if not printer.user.telegram_chat_id:
        return

    try:
        photo = requests.get(printer.pic['img_url']).content
    except:
        photo = None

    action = ''
    button_list = ['more_info']
    if print_paused:
        action = 'The print is paused.'
        button_list = ['cancel', 'resume', 'do_not_ask', 'more_info']
    elif printer.action_on_failure == Printer.PAUSE and is_warning:
        action = 'Printer is NOT paused because The Detective is not very sure about it.'
        button_list = ['cancel', 'more_info']

    notification_text = f"""Hi {printer.user.first_name or ''},

_The Spaghetti Detective_ spotted some suspicious activity on your printer *{printer.name}*.

{action}"""

    send_telegram_notification(printer, notification_text, photo, buttons=button_list)


def send_print_notification(print_id):
    _print = Print.objects.select_related('printer__user').get(id=print_id)
    if _print.is_canceled():
        if not _print.printer.user.notify_on_canceled:
            return
    else:
        if not _print.printer.user.notify_on_done:
            return

    if _print.printer.user.print_notification_by_email:
        send_print_notification_email(_print)

    if _print.printer.user.print_notification_by_pushbullet:
        send_print_notification_pushbullet(_print)

    if _print.printer.user.print_notification_by_telegram:
        send_print_notification_telegram(_print)

def send_print_notification_email(_print):
    subject = f'{_print.filename} is canceled.' if _print.is_canceled() else f'🙌 {_print.filename} is ready.'
    ctx = {
        'print': _print,
        'print_time': str(_print.ended_at() - _print.started_at).split('.')[0],
        'timelapse_link': site.build_full_url('/prints/'),
    }
    unsub_url = site.build_full_url(f'/unsubscribe_email/?unsub_token={_print.printer.user.unsub_token}&list=print_notification')
    send_email(
        _print.printer.user,
        subject,
        unsub_url,
        'email/print_notification.html',
        ctx,
        img_url=_print.printer.pic['img_url'] if _print.printer.pic else None,
        )

def send_print_notification_telegram(_print):
    if not _print.printer.user.telegram_chat_id:
        return

    try:
        photo = requests.get(_print.printer.pic['img_url']).content
    except:
        photo = None

    notification_text = f"""Hi {_print.printer.user.first_name or ''},

Your print job *{_print.filename}* {'has been canceled' if _print.is_canceled() else 'is done'} on printer {_print.printer.name}.
"""
    send_telegram_notification(_print.printer, notification_text, photo)

def send_print_notification_pushbullet(_print):
    if not _print.printer.user.has_valid_pushbullet_token():
        return

    pb = Pushbullet(_print.printer.user.pushbullet_access_token)

    title = 'The Spaghetti Detective - Print job notification'
    link = site.build_full_url('/')
    body = f"Your print job {_print.filename} {'has been canceled' if _print.is_canceled() else 'is done'} on printer {_print.printer.name}."
    file_url = None
    try:
        file_url = _print.printer.pic['img_url']
        if not ipaddress.ip_address(urlparse(file_url).hostname).is_global:
            pb.upload_file(requests.get(file_url).content, 'Snapshot.jpg')
    except:
        pass

    if file_url:
        pb.push_file(file_url=file_url, file_name="Snapshot.jpg", file_type="image/jpeg", body=body, title=title)
    else:
        pb.push_link(title, link, body)

# Helpers

def send_email(user, subject, unsub_url, template_path, ctx, img_url=None):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    attachments = []
    if img_url:
        # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
        try:
            if not ipaddress.ip_address(urlparse(img_url).hostname).is_global:
                attachments = [('Image.jpg', requests.get(img_url).content, 'image/jpeg')]
        except:
            pass

        ctx['img_url'] = None if attachments else img_url

    # By default email verification should be required for notifications but
    # maybe users will want to disable it on private servers
    if settings.ACCOUNT_EMAIL_VERIFICATION != 'none':
        emails = EmailAddress.objects.filter(user=user, verified=True)
    else:
        emails = EmailAddress.objects.filter(user=user)

    for email in emails:
        ctx['unsub_url'] = unsub_url
        message = get_template(template_path).render(ctx)
        msg = EmailMessage(subject, message,
            to=(email.email,),
            from_email=settings.DEFAULT_FROM_EMAIL,
            attachments=attachments,
            headers = {'List-Unsubscribe': '<{}>, <mailto:support@thespaghettidetective.com?subject=Unsubscribe_notification>'.format(unsub_url)},)
        msg.content_subtype = 'html'
        msg.send()
