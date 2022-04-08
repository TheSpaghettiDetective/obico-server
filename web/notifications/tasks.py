from typing import Dict, Optional, Tuple
import logging

from app.models import Printer, Print
from app.tasks import will_record_timelapse, compile_timelapse

from celery import shared_task  # type: ignore


from .handlers import handler
from . import events

LOGGER = logging.getLogger(__name__)


@shared_task
def send_printer_notifications(
    printer_id: int,
    event_name: str,
    event_data: Dict,
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

    if event_name in events.PRINT_END_EVENTS:
        assert cur_print, "cannot process print end event without a print"

        if not will_record_timelapse(cur_print):
            LOGGER.warning(f'will not record timelapse, {event_name} is suppressed for print (pk: {cur_print.id}')
            return

        compile_timelapse.delay(cur_print.id)

    handler.send_printer_notifications(
        event_name=event_name,
        event_data=event_data,
        printer=printer,
        print_=cur_print,
        poster_url=poster_url or '',
        extra_context=extra_context,
        plugin_names=plugin_names,
    )
