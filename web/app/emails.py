from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings
import logging

from lib import site

LOGGER = logging.getLogger(__name__)

def send_failure_alert(printer):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    subject = 'Your print {} may be failing on {}'.format(printer.current_print_filename or '', printer.name)
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'printer': printer,
        'view_link': site.build_full_url('/printers/'),
        'cancel_link': site.build_full_url('/printers/{}/cancel'.format(printer.id)),
        'resume_link': site.build_full_url('/printers/{}/resume'.format(printer.id)),
    }

    message = get_template('email/failure_alert.html').render(ctx)
    msg = EmailMessage(subject, message, to=(printer.user.email,), from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
