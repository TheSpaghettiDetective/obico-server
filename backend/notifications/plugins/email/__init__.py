from typing import Dict, Optional, List
import smtplib
import logging
import backoff  # type: ignore
import os

from django.conf import settings
from django.template.base import Template
from django.template.loader import get_template
from django.core.mail import EmailMessage

from allauth.account.admin import EmailAddress  # type: ignore
from lib import site as site

from notifications.handlers import handler
from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    notification_types,
)

LOGGER = logging.getLogger(__name__)


class EmailNotificationPlugin(BaseNotificationPlugin):

    def env_vars(self) -> Dict:
        return {
            'EMAIL_HOST': {
                'is_required': True,
                'is_set': 'EMAIL_HOST' in os.environ,
                'value': os.environ.get('EMAIL_HOST'),
            },
            'EMAIL_PORT': {
                'is_required': True,
                'is_set': 'EMAIL_PORT' in os.environ,
                'value': os.environ.get('EMAIL_PORT'),
            },
            'EMAIL_HOST_USER': {
                'is_required': True,
                'is_set': 'EMAIL_HOST_USER' in os.environ,
            },
            'EMAIL_HOST_PASSWORD': {
                'is_required': True,
                'is_set': 'EMAIL_HOST_PASSWORD' in os.environ,
            },
        }

    def get_printer_notification_subject(self, context: PrinterNotificationContext) -> str:
        notification_type = context.notification_type
        notification_data = context.notification_data

        if notification_type == notification_types.PrintStarted:
            text = f"{context.print.filename} started"
        elif notification_type == notification_types.PrintDone:
            text = f"🙌 {context.print.filename} is ready"
        elif notification_type == notification_types.PrintCancelled:
            text = f"{context.print.filename} is canceled"
        elif notification_type == notification_types.PrintPaused:
            text = f"{context.print.filename} is paused"
        elif notification_type == notification_types.PrintResumed:
            text = f"{context.print.filename} is resumed"
        elif notification_type == notification_types.FilamentChange:
            text = f"{context.print.filename} requires filament change"
        elif notification_type == notification_types.HeaterCooledDown:
            text = (
                f"Heater {self.b(notification_data['name'])} "
                f"has cooled down to {self.b(str(notification_data['actual']) + '℃')}"
            )
        elif notification_type == notification_types.HeaterTargetReached:
            text = (
                f"Heater {self.b(notification_data['name'])} "
                f"has reached target temperature {self.b(str(notification_data['actual']) + '℃')} "
            )
        else:
            return ''

        return text

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        if not settings.EMAIL_HOST:
            LOGGER.warn("Email settings are missing. Ignored send requests")
            return

        template_name = 'email/FailureAlert.html'
        tpl = get_template(template_name)

        mailing_list: str = 'failure_alert'
        unsub_url = site.build_full_url(
            f'/unsubscribe_email/?unsub_token={context.user.unsub_token}&list={mailing_list}'
        )
        headers = {
            'List-Unsubscribe': f'<{unsub_url}>, <mailto:support@obico.io?subject=Unsubscribe_{mailing_list}>'
        }

        ctx = context.extra_context or {}
        ctx.update(
            printer=context.printer,
            print_paused=context.print_paused,
            is_warning=context.is_warning,
            view_link=site.build_full_url('/printers/'),
            cancel_link=site.build_full_url('/prints/{}/cancel/'.format(context.print.id)),
            resume_link=site.build_full_url('/prints/{}/resume/'.format(context.print.id)),
            unsub_url=unsub_url,
            context=context,
        )

        attachments = []
        if context.img_url:
            # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
            try:
                if not settings.SITE_IS_PUBLIC:
                    attachments = [('Image.jpg', requests.get(context.img_url).content, 'image/jpeg')]
            except:
                pass

            ctx['img_url'] = None if attachments else context.img_url

        message = tpl.render(ctx)
        subject = 'Your print {} on {} {}.'.format(
            context.print.filename,
            context.printer.name,
            'smells fishy' if context.is_warning else 'is probably failing')

        self._send_emails(
            user_id=context.user.id,
            subject=subject,
            message=message,
            headers=headers,
            attachments=attachments,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        if not settings.EMAIL_HOST:
            LOGGER.warn("Email settings are missing. Ignored send requests")
            return

        template_name = f'email/{context.notification_type}.html'
        tpl = get_template(template_name)
        if not tpl:
            LOGGER.debug(f'Missing template "{template_name}", ignoring event "{context.notification_type}"')
            return

        subject = self.get_printer_notification_subject(context)
        mailing_list: str = context.feature.name.replace('notify_on_', '')

        unsub_url = site.build_full_url(
            f'/unsubscribe_email/?unsub_token={context.user.unsub_token}&list={mailing_list}'
        )
        headers = {
            'List-Unsubscribe': f'<{unsub_url}>, <mailto:support@obico.io?subject=Unsubscribe_{mailing_list}>'
        }

        ctx = context.extra_context or {}
        ctx.update(
            timelapse_link=site.build_full_url(f'/prints/{context.print.id}/'),
            user_pref_url=site.build_full_url('/user_preferences/notification_email/'),
            unsub_url=unsub_url,
            context=context,
        )

        if context.print.ended_at and context.print.started_at:
            ctx['print_time'] = str(context.print.ended_at - context.print.started_at).split('.')[0]

        attachments = []
        if context.img_url:
            # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
            try:
                if not settings.SITE_IS_PUBLIC:
                    attachments = [('Image.jpg', requests.get(context.img_url).content, 'image/jpeg')]
            except:
                pass

            ctx['img_url'] = None if attachments else context.img_url

        message = tpl.render(ctx)
        self._send_emails(
            user_id=context.user.id,
            subject=subject,
            message=message,
            headers=headers,
            attachments=attachments,
        )

    def _send_emails(self, user_id: int, subject: str, message: str, headers: Dict, verified_only: bool = True, attachments: Optional[List] = None) -> None:
        if not settings.EMAIL_HOST:
            LOGGER.warn("Email settings are missing. Ignored send requests")
            return

        # By default email verification should be required for notifications but
        # maybe users will want to disable it on private servers
        if settings.ACCOUNT_EMAIL_VERIFICATION != 'none' and verified_only:
            emails = EmailAddress.objects.filter(user_id=user_id, verified=True)
        else:
            emails = EmailAddress.objects.filter(user_id=user_id)

        for email in emails:
            self._send_email(email=email.email, subject=subject, message=message, attachments=attachments, headers=headers)

    @backoff.on_exception(
        backoff.expo,
        (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused, smtplib.SMTPResponseException, ),
        max_tries=3
    )
    def _send_email(self, email: str, subject: str, message: str, headers: Dict, attachments: Optional[List]) -> None:
        if not settings.EMAIL_HOST:
            LOGGER.warn("Email settings are missing. Ignored send requests")
            return

        msg = EmailMessage(
            subject,
            message,
            to=(email,),
            from_email=settings.DEFAULT_FROM_EMAIL,
            attachments=attachments or [],
            headers=headers,
        )
        msg.content_subtype = 'html'
        msg.send()


def __load_plugin__():
    return EmailNotificationPlugin()
