from allauth.account.admin import EmailAddress
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings
from pushbullet import Pushbullet, PushbulletError, PushError
import requests
import logging
from urllib.parse import urlparse
import ipaddress

from app.models import Printer
from app.telegram_bot import send_notification as send_telegram_notification
from lib import site

LOGGER = logging.getLogger(__name__)

def send_failure_alert(printer, is_warning=True, print_paused=False):
    LOGGER.info(f'Sending alerts to {printer.user.id}')

    # Fixme: any exception will cause subsequent notification channel to be tried at all.
    # This is also why SMS is currently at the end, since it'll fail with exception when area code is not allowed.
    send_failure_alert_email(printer, is_warning, print_paused)
    send_failure_alert_pushbullet(printer, is_warning, print_paused)
    send_failure_alert_telegram(printer, is_warning, print_paused)
    if printer.user.is_pro:
        send_failure_alert_sms(printer, is_warning, print_paused)

def send_failure_alert_email(printer, is_warning, print_paused):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
    try:
        if ipaddress.ip_address(urlparse(printer.pic['img_url']).hostname).is_global:
            attachments = []
        else:
            attachments = [('Detected Failure.jpg', requests.get(printer.pic['img_url']).content, 'image/jpeg')]
    except:
        attachments = []

    subject = 'Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'printer': printer,
        'print_paused': print_paused,
        'is_warning': is_warning,
        'edit_link': site.build_full_url('/printers/{}'.format(printer.id)),
        'view_link': site.build_full_url('/printers/'),
        'cancel_link': site.build_full_url('/printers/{}/cancel/'.format(printer.id)),
        'resume_link': site.build_full_url('/printers/{}/resume/'.format(printer.id)),
        'insert_img': len(attachments) == 0,
    }

    # By default email verification should be required for notifications but
    # maybe users will want to disable it on private servers
    if settings.ACCOUNT_EMAIL_VERIFICATION != 'none':
        emails = EmailAddress.objects.filter(user=printer.user, verified=True)
    else:
        emails = EmailAddress.objects.filter(user=printer.user)
    for email in emails:
        unsub_url = 'https://app.thespaghettidetective.com/ent/email_unsubscribe/?list=notification&email={}'.format(email)
        ctx['unsub_url'] = unsub_url
        message = get_template('email/failure_alert.html').render(ctx)
        msg = EmailMessage(subject, message,
            to=(email.email,),
            from_email=from_email,
            attachments=attachments,
            headers = {'List-Unsubscribe': '<{}>, <mailto:support@thespaghettidetective.com?subject=Unsubscribe_notification>'.format(unsub_url)},)
        msg.content_subtype = 'html'
        msg.send()

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
    title = 'The Spaghetti Detective - Your print {} on {} {}.'.format(
        printer.current_print.filename or '',
        printer.name,
        'smells fishy' if is_warning else 'is probably failing')
    link = site.build_full_url('/')
    body = '{}\nGo check it at: {}'.format(pausing_msg, link)

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

    notification_text = f"""Hi *{printer.user.first_name or ''}*,

_The Spaghetti Detective_ spotted some suspicious activity on your printer *{printer.name}*.

{action}"""

    send_telegram_notification(printer, button_list, notification_text, photo)
