from typing import Dict, Optional, Tuple
import logging
from sentry_sdk import set_user
from celery import shared_task  # type: ignore

from app.models import Printer, Print
from app.tasks import will_record_timelapse, compile_timelapse
from .handlers import handler
from . import notification_types

LOGGER = logging.getLogger(__name__)


@shared_task
def send_printer_notifications(
    printer_id: int,
    notification_type: str,
    notification_data: Dict,
    print_id: Optional[int],
    extra_context: Optional[Dict] = None,
    plugin_names: Tuple[str, ...] = (),
    **kwargs
) -> None:
    extra_context = extra_context or {}

    if print_id:
        cur_print = Print.objects.all_with_deleted().select_related('printer', 'printer__user').filter(
            id=print_id, printer_id=printer_id).first()
        if not cur_print: # Printer may be deleted or archived
            return
        printer = cur_print.printer
    else:
        cur_print = None
        printer = Printer.objects.select_related('user').filter(id=printer_id).first()
        if not printer: # Printer may be deleted or archived
            return

    set_user({"id": printer.user_id})

    handler.send_printer_notifications(
        notification_type=notification_type,
        notification_data=notification_data,
        printer=printer,
        print_=cur_print,
        extra_context=extra_context,
        plugin_names=plugin_names,
    )
