from allauth.account.admin import EmailAddress
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from django.utils import timezone
from twilio.rest import Client
from django.conf import settings
from pushbullet import Pushbullet, PushbulletError, PushError
import requests
import logging
from urllib.parse import urlparse
import ipaddress
from sentry_sdk import capture_exception
import smtplib
import backoff

from lib.file_storage import save_file_obj
from lib.utils import save_print_snapshot, last_pic_of_print
from app.models import Printer, Print
from app.telegram_bot import send_notification as send_telegram_notification
from lib import site

LOGGER = logging.getLogger(__name__)


def send_failure_alert(printer, is_warning=True, print_paused=False):
    LOGGER.info(f'Printer {printer.user.id} {"smells fishy" if is_warning else "is probably failing"}. Sending Alerts')
    if not printer.current_print:
        LOGGER.warn(f'Trying to alert on printer without current print. printer_id: {printer.id}')
        return

    (_, rotated_jpg_url) = save_print_snapshot(
        printer.current_print,
        last_pic_of_print(printer.current_print, 'tagged'),
        unrotated_jpg_path=None,
        rotated_jpg_path=f'snapshots/{printer.id}/{printer.current_print.id}/{str(timezone.now().timestamp())}_rotated.jpg')

    # Calls wrapped in individual try/except because anyone of them could fail, and we still want the flow to continue

    try:
        if printer.user.alert_by_email:
            send_failure_alert_email(printer, rotated_jpg_url, is_warning, print_paused)
    except:
        capture_exception()

    try:
        send_failure_alert_pushbullet(printer, rotated_jpg_url, is_warning, print_paused)
    except:
        capture_exception()

    try:
        send_failure_alert_telegram(printer, rotated_jpg_url, is_warning, print_paused)
    except:
        capture_exception()

    try:
        if printer.user.is_pro and printer.user.alert_by_sms:
            send_failure_alert_sms(printer, is_warning, print_paused)
    except:
        capture_exception()

    try:
        if printer.user.is_pro:
            send_failure_alert_slack(printer, rotated_jpg_url, is_warning, print_paused)
    except:
        capture_exception()


def send_failure_alert_email(printer, rotated_jpg_url, is_warning, print_paused):
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
        'cancel_link': site.build_full_url('/prints/{}/cancel/'.format(printer.current_print_id)),
        'resume_link': site.build_full_url('/prints/{}/resume/'.format(printer.current_print_id)),
    }

    send_email(
        user=printer.user,
        subject=subject,
        mailing_list='alert',
        template_path='email/failure_alert.html',
        ctx=ctx,
        img_url=rotated_jpg_url,
    )


def send_failure_alert_sms(printer, is_warning, print_paused):
    if not settings.TWILIO_ENABLED:
        LOGGER.warn("Twilio settings are missing. Ignored send requests")
        return

    if not printer.user.sms_eligible():
        return

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

    send_sms(msg, to_number)


def send_failure_alert_pushbullet(printer, rotated_jpg_url, is_warning, print_paused):
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
            file_url = rotated_jpg_url
            if not ipaddress.ip_address(urlparse(file_url).hostname).is_global:
                pb.upload_file(requests.get(file_url).content, 'Detected Failure.jpg')
        except:
            pass

        if file_url:
            pb.push_file(file_url=file_url, file_name="Detected Failure.jpg", file_type="image/jpeg", body=body, title=title)
        else:
            pb.push_link(title, link, body)
    except (PushError, PushbulletError) as e:
        LOGGER.error(e)


def send_failure_alert_telegram(printer, rotated_jpg_url, is_warning, print_paused):
    if not printer.user.telegram_chat_id:
        return

    try:
        photo = requests.get(rotated_jpg_url).content
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

    try:
        send_telegram_notification(printer, notification_text, photo, buttons=button_list)
    except requests.ConnectionError as e:
        LOGGER.error(e)


def send_failure_alert_slack(printer, rotated_jpg_url, is_warning, print_paused):
    if not printer.user.slack_access_token:
        return

    req = requests.get(
        url='https://slack.com/api/conversations.list',
        params={
            'token': printer.user.slack_access_token,
            'types': 'public_channel,private_channel'
        })
    req.raise_for_status()
    slack_channel_ids = [c['id'] for c in req.json()['channels'] if c['is_member']]

    for slack_channel_id in slack_channel_ids:
        msg = {
            "channel": slack_channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*The Spaghetti Detective - Failure alert*\n\nYour print {printer.current_print.filename or ''} on {printer.name} {'smells fishy' if is_warning else 'is probably failing'}.\nThe printer is {'paused' if print_paused else 'NOT paused'}.\n<{site.build_full_url('/printers/')}|Check it out.>"
                    }
                }
            ]
        }
        try:
            msg['blocks'].append(
                {
                    "type": "image",
                    "image_url": rotated_jpg_url,
                    "alt_text": "Print snapshot"
                }
            )
        except:
            pass

        req = requests.post(
            url='https://slack.com/api/chat.postMessage',
            headers={'Authorization': f'Bearer {printer.user.slack_access_token}'},
            json=msg
        )
        req.raise_for_status()


def send_print_notification(_print, extra_ctx={}):
    if _print.is_canceled():
        if not _print.printer.user.notify_on_canceled:
            return
    else:
        if not _print.printer.user.notify_on_done:
            return

    # Calls wrapped in individual try/except because anyone of them could fail, and we still want the flow to continue

    try:
        if _print.printer.user.print_notification_by_email:
            send_print_notification_email(_print, extra_ctx)
    except:
        capture_exception()

    try:
        if _print.printer.user.print_notification_by_pushbullet:
            send_print_notification_pushbullet(_print)
    except:
        capture_exception()

    try:
        if _print.printer.user.print_notification_by_telegram:
            send_print_notification_telegram(_print)
    except:
        capture_exception()

    try:
        if _print.printer.user.is_pro:
            send_print_notification_slack(_print)
    except:
        capture_exception()


def send_print_notification_email(_print, extra_ctx={}):
    subject = f'{_print.filename} is canceled.' if _print.is_canceled() else f'🙌 {_print.filename} is ready.'
    ctx = {
        'print': _print,
        'print_time': str(_print.ended_at() - _print.started_at).split('.')[0],
        'timelapse_link': site.build_full_url(f'/prints/{_print.id}/'),
    }
    ctx.update(extra_ctx)
    send_email(
        user=_print.printer.user,
        subject=subject,
        mailing_list='print_notification',
        template_path='email/print_notification.html',
        ctx=ctx,
        img_url=_print.poster_url,
    )


def send_print_notification_telegram(_print):
    if not _print.printer.user.telegram_chat_id:
        return

    try:
        photo = requests.get(_print.poster_url).content
    except:
        photo = None

    notification_text = f"""Hi {_print.printer.user.first_name or ''},

Your print job *{_print.filename}* {'has been canceled' if _print.is_canceled() else 'is done'} on printer {_print.printer.name}.
"""
    try:
        send_telegram_notification(_print.printer, notification_text, photo)
    except requests.ConnectionError as e:
        LOGGER.error(e)


def send_print_notification_pushbullet(_print):
    if not _print.printer.user.has_valid_pushbullet_token():
        return

    pb = Pushbullet(_print.printer.user.pushbullet_access_token)

    title = 'The Spaghetti Detective - Print job notification'
    link = site.build_full_url('/')
    body = f"Your print job {_print.filename} {'has been canceled' if _print.is_canceled() else 'is done'} on printer {_print.printer.name}."
    file_url = None
    try:
        file_url = _print.poster_url
        if not ipaddress.ip_address(urlparse(file_url).hostname).is_global:
            pb.upload_file(requests.get(file_url).content, 'Snapshot.jpg')
    except:
        pass

    try:
        if file_url:
            pb.push_file(file_url=file_url, file_name="Snapshot.jpg", file_type="image/jpeg", body=body, title=title)
        else:
            pb.push_link(title, link, body)
    except (PushError, PushbulletError) as e:
        LOGGER.error(e)


def send_print_notification_slack(_print):
    if not _print.printer.user.slack_access_token:
        return

    req = requests.get(
        url='https://slack.com/api/conversations.list',
        params={
            'token': _print.user.slack_access_token,
            'types': 'public_channel,private_channel'
        })
    req.raise_for_status()
    slack_channel_ids = [c['id'] for c in req.json()['channels'] if c['is_member']]

    for slack_channel_id in slack_channel_ids:
        msg = {
            "channel": slack_channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*The Spaghetti Detective - Print job notification*\n\n*G-Code*: {_print.filename} \n*Status*: {'Canceled' if _print.is_canceled() else 'Finished'}\n*Printer*: <{site.build_full_url('/printers/')}|{_print.printer.name}>"
                    }
                }
            ]
        }
        if _print.poster_url:
            msg['blocks'].append(
                {
                    "type": "image",
                    "image_url": _print.poster_url,
                    "alt_text": "Print snapshot"
                }
            )

        req = requests.post(
            url='https://slack.com/api/chat.postMessage',
            headers={'Authorization': f'Bearer {_print.user.slack_access_token}'},
            json=msg
        )
        req.raise_for_status()


# Helpers
@backoff.on_exception(backoff.expo,
                      (smtplib.SMTPServerDisconnected,
                       smtplib.SMTPSenderRefused,
                       smtplib.SMTPResponseException,),
                      max_tries=3)
def send_email(user, subject, mailing_list, template_path, ctx, img_url=None, verified_only=True, attachment=None):
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
    if settings.ACCOUNT_EMAIL_VERIFICATION != 'none' and verified_only:
        emails = EmailAddress.objects.filter(user=user, verified=True)
    else:
        emails = EmailAddress.objects.filter(user=user)

    unsub_url = site.build_full_url(f'/unsubscribe_email/?unsub_token={user.unsub_token}&list={mailing_list}')
    for email in emails:
        ctx['unsub_url'] = unsub_url
        message = get_template(template_path).render(ctx)
        msg = EmailMessage(
            subject,
            message,
            to=(email.email,),
            from_email=settings.DEFAULT_FROM_EMAIL,
            attachments=attachments,
            headers={'List-Unsubscribe': f'<{unsub_url}>, <mailto:support@thespaghettidetective.com?subject=Unsubscribe_{mailing_list}>'},)
        msg.content_subtype = 'html'
        if attachment:
            msg.attach_file(attachment)
        msg.send()


def send_sms(msg, to_number):
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    from_number = settings.TWILIO_FROM_NUMBER

    twilio_client.messages.create(body=msg, to=to_number, from_=from_number)
