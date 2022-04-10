from typing import Dict, Optional, Tuple
import logging

from app.models import Printer, Print
from app.tasks import will_record_timelapse, compile_timelapse

from celery import shared_task  # type: ignore


from .handlers import handler
from . import notification_types

LOGGER = logging.getLogger(__name__)


@shared_task
def send_printer_notifications(
    printer_id: int,
    notification_type: str,
    notification_data: Dict,
    print_id: Optional[int],
    poster_url: str = '',
    extra_context: Optional[Dict] = None,
    plugin_names: Tuple[str, ...] = (),
    **kwargs
) -> None:
    extra_context = extra_context or {}

    if print_id:
        # FIXME any additional filter? User.is_active?
        cur_print = Print.objects.all_with_deleted().select_related('printer', 'printer__user').get(
            id=print_id, printer_id=printer_id)
        printer = cur_print.printer
    else:
        cur_print = None
        # FIXME any additional filter? User.is_active?
        printer = Printer.objects.select_related('user').get(id=printer_id)

    handler.send_printer_notifications(
        notification_type=notification_type,
        notification_data=notification_data,
        printer=printer,
        print_=cur_print,
        poster_url=poster_url or '',
        extra_context=extra_context,
        plugin_names=plugin_names,
    )
