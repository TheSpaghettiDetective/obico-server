from typing import Dict, Optional, Tuple
import logging
from sentry_sdk import set_user
from celery import shared_task  # type: ignore
from sentry_sdk import capture_exception

from app.models import Printer, Print, NotificationSetting, User
from app.tasks import will_record_timelapse, compile_timelapse
from .handlers import handler
from lib.utils import get_rotated_pic_url
from .plugin import (
    BaseNotificationPlugin,
    PrinterNotificationContext, FailureAlertContext,
    UserContext, PrintContext, PrinterContext, TestMessageContext,
    Feature,
)

LOGGER = logging.getLogger(__name__)


@shared_task
def send_printer_notifications(
    printer_id: int,
    notification_type: str,
    print_id: Optional[int],
    extra_context: Optional[Dict] = None,
    plugin_names: Tuple[str, ...] = (),
    **kwargs
) -> None:
    extra_context = extra_context or {}

    if print_id:
        print_ = Print.objects.all_with_deleted().select_related('printer', 'printer__user').filter(
            id=print_id, printer_id=printer_id).first()
        if not print_: # Printer may be deleted or archived
            return
        printer = print_.printer
    else:
        print_ = None
        printer = Printer.objects.select_related('user').filter(id=printer_id).first()
        if not printer: # Printer may be deleted or archived
            return

    set_user({"id": printer.user_id})

    feature = handler.feature_for_notification_type(notification_type)
    if not feature:
        return

    if plugin_names:
        names = list(set(handler.notification_plugin_names()) & set(plugin_names))
    else:
        names = handler.notification_plugin_names()

    # select matching, enabled & configured
    nsettings = list(NotificationSetting.objects.filter(
        user_id=printer.user_id,
        enabled=True,
        name__in=names,
        **{feature.name: True}
    ))

    if not nsettings:
        LOGGER.debug("no matching NotificationSetting objects, ignoring printer notification")
        return

    if print_ and print_.poster_url:
        img_url = print_.poster_url
    else:
        img_url = get_rotated_pic_url(printer, force_snapshot=True)

    user_ctx = handler.get_user_context(printer.user)
    printer_ctx = handler.get_printer_context(printer)
    print_ctx = handler.get_print_context(print_)

    for nsetting in nsettings:
        LOGGER.debug(f'forwarding event {"notification_type"} to plugin "{nsetting.name}" (pk: {nsetting.pk})')
        try:
            plugin = handler.notification_plugin_by_name(nsetting.name)
            if not plugin:
                continue

            context = PrinterNotificationContext(
                feature=feature,
                config=nsetting.config,
                user=user_ctx,
                printer=printer_ctx,
                print=print_ctx,
                notification_type=notification_type,
                extra_context=extra_context or {},
                img_url=img_url,
            )

            plugin = handler.notification_plugin_by_name(nsetting.name)
            if not plugin:
                return

            if not handler.should_plugin_handle_notification_type(
                plugin.instance,
                nsetting,
                context.notification_type,
            ):
                return

            plugin.instance.send_printer_notification(context=context)

        except NotImplementedError:
            pass


@shared_task
def send_failure_alerts(
    print_id: int,
    is_warning: bool,
    print_paused: bool,
    img_url: str,
) -> None:

    print_ = Print.objects.all_with_deleted().select_related('printer', 'printer__user').filter(id=print_id).first()
    if not print_: # Printer may be deleted or archived
        return
    printer = print_.printer

    try:
        mobile_notifications.send_failure_alert(printer, img_url, is_warning, print_paused)
    except Exception:
        capture_exception()

    # select matching, enabled & configured
    nsettings = list(NotificationSetting.objects.filter(
        user_id=printer.user_id,
        enabled=True,
        name__in=handler.notification_plugin_names(),
        notify_on_failure_alert=True
    ))

    if not nsettings:
        LOGGER.debug("no matching NotificationSetting objects, ignoring failure alert")
        return

    user_ctx = handler.get_user_context(printer.user)
    printer_ctx = handler.get_printer_context(printer)
    print_ctx = handler.get_print_context(print_)

    for nsetting in nsettings:
        LOGGER.debug(f'forwarding failure alert to plugin "{nsetting.name}" (pk: {nsetting.pk})')
        try:
            plugin = handler.notification_plugin_by_name(nsetting.name)
            if not plugin:
                continue

            context = FailureAlertContext(
                config=nsetting.config,
                user=user_ctx,
                printer=printer_ctx,
                print=print_ctx,
                is_warning=is_warning,
                print_paused=print_paused,
                extra_context={},
                img_url=img_url,
            )

            plugin.instance.send_failure_alert(context=context)
        except NotImplementedError:
            pass
