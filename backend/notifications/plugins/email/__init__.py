from typing import Dict, Optional, List
import smtplib
import logging
import backoff  # type: ignore
import os
import requests
from django.conf import settings
from django.template.base import Template
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.core.mail import EmailMessage
from allauth.account.models import EmailAddress

from lib import syndicate
from notifications.handlers import handler
from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    notification_types,
    UserContext,
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
        extra_context = context.extra_context

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
            text = f"Printer needs attention - {context.print.filename if context.print else ''}"
        elif notification_type == notification_types.HeaterCooledDown:
            text = (
                f"Heater {self.b(extra_context['heater_name'])} "
                f"has cooled down to {self.b(str(extra_context['heater_actual']) + '℃')}"
            )
        elif notification_type == notification_types.HeaterTargetReached:
            text = (
                f"Heater {self.b(extra_context['heater_name'])} "
                f"has reached target temperature {self.b(str(extra_context['heater_target']) + '℃')} "
            )
        else:
            return ''

        return text

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        template_path = 'email/FailureAlert.html'
        mailing_list: str = 'failure_alert'

        email_ctx = context.extra_context or {}
        email_ctx.update(
            printer=context.printer,
            print_paused=context.print_paused,
            is_warning=context.is_warning,
            view_link=syndicate.build_full_url_for_syndicate('/printers/', context.user.syndicate_name),
            cancel_link=syndicate.build_full_url_for_syndicate('/prints/{}/cancel/'.format(context.print.id), context.user.syndicate_name),
            resume_link=syndicate.build_full_url_for_syndicate('/prints/{}/resume/'.format(context.print.id), context.user.syndicate_name),
        )

        subject = 'Your print {} on {} {}.'.format(
            context.print.filename,
            context.printer.name,
            'smells fishy' if context.is_warning else 'is probably failing')

        self.send_emails(
            user=context.user,
            subject=subject,
            mailing_list=mailing_list,
            template_path=template_path,
            ctx=email_ctx,
            img_url=context.img_url,
        )

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        template_path = f'email/{context.notification_type}.html'
        subject = self.get_printer_notification_subject(context)
        mailing_list: str = context.feature.name.replace('notify_on_', '')

        email_ctx = context.extra_context or {}
        email_ctx.update(
            printer=context.printer,
            print=context.print,
            timelapse_link=syndicate.build_full_url_for_syndicate(f'/prints/{context.print.id}/', context.user.syndicate_name),
            user_pref_url=syndicate.build_full_url_for_syndicate('/user_preferences/notification_email/', context.user.syndicate_name),
        )

        if context.print.ended_at and context.print.started_at:
            email_ctx['print_time'] = str(context.print.ended_at - context.print.started_at).split('.')[0]

        self.send_emails(
            user=context.user,
            subject=subject,
            mailing_list=mailing_list,
            template_path=template_path,
            ctx=email_ctx,
            img_url=context.img_url,
        )

    def send_emails(self,
            user: UserContext,
            subject: str,
            mailing_list: str,
            template_path: str,
            ctx: Dict,
            img_url: str = None,
            verified_only: bool = True,
            attachments: Optional[List] = None) -> None:

        attachments = attachments or []

        tpl = None
        layout_template_path='email/Layout.html'
        if user.syndicate_name and user.syndicate_name != 'base':
            layout_template_path=f'{user.syndicate_name}/email/Layout.html'
            try:
                tpl = get_template(f'{user.syndicate_name}/{template_path}')
            except TemplateDoesNotExist:
                pass # Fall back to default template

        if not tpl:
            tpl = get_template(template_path)

        ctx['layout_template_path'] = layout_template_path
        ctx['user'] = user
        # Strip any trailing slashes from mailing_list to prevent URL parsing issues
        clean_mailing_list = mailing_list.rstrip('/')
        unsub_url = syndicate.build_full_url_for_syndicate(
            f'/unsubscribe_email/?unsub_token={user.unsub_token}&list={clean_mailing_list}', user.syndicate_name)
        ctx['unsub_url'] = unsub_url

        headers = {
            'List-Unsubscribe': f'<{unsub_url}>, <mailto:support@obico.io?subject=Unsubscribe_{clean_mailing_list}>'
        }

        if img_url:
            # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/issues/43
            try:
                if not settings.SITE_IS_PUBLIC:
                    attachments.append(('Image.jpg', requests.get(img_url).content, 'image/jpeg'))
                else:
                    ctx['img_url'] = img_url
            except Exception as e:
                LOGGER.warn("Could not attach image: " + str(e))
                ctx['img_url'] = img_url

        message = tpl.render(ctx)

        # By default email verification should be required for notifications but
        # maybe users will want to disable it on private servers
        if settings.ACCOUNT_EMAIL_VERIFICATION != 'none' and verified_only:
            emails = EmailAddress.objects.filter(user_id=user.id, verified=True)
        else:
            emails = EmailAddress.objects.filter(user_id=user.id)

        for email in emails:
            self._send_email(email=email.email, subject=subject, message=message, attachments=attachments, headers=headers, user=user)

    @backoff.on_exception(
        backoff.expo,
        (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused, smtplib.SMTPResponseException, ),
        max_tries=3
    )
    def _send_email(self, email: str, subject: str, message: str, headers: Dict, attachments: Optional[List], user: UserContext) -> None:
        if not settings.EMAIL_HOST:
            LOGGER.warn("Email settings are missing. Ignored send requests")
            return

        from_email = syndicate.settings_for_syndicate(user.syndicate_name).get('from_email', settings.DEFAULT_FROM_EMAIL)

        msg = EmailMessage(
            subject,
            message,
            to=(email,),
            from_email=from_email,
            attachments=attachments or [],
            headers=headers,
        )
        msg.content_subtype = 'html'
        msg.send()


def __load_plugin__():
    return EmailNotificationPlugin()
