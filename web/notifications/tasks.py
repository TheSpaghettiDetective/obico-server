from typing import Dict, Optional, Tuple
import logging

from app.models import Printer, Print

from celery import shared_task  # type: ignore

from .handlers import handler


LOGGER = logging.getLogger(__name__)


@shared_task
def send_printer_notifications(
    printer_id: int,
    event_name: str,
    event_data: Dict,
    print_id: Optional[int],
    poster_url: str = '',
    plugin_names: Tuple[str, ...] = (),
    **kwargs
) -> None:
    if print_id:
        # FIXME any additional filter? User.is_active?
        print_ = Print.objects.select_related('printer', 'printer__user').get(
            id=print_id, printer_id=printer_id)
        printer = print_.printer
    else:
        print_ = None
        # FIXME any additional filter? User.is_active?
        printer = Printer.objects.select_related('user').get(id=printer_id)

    handler.send_printer_notifications(
        event_name=event_name,
        event_data=event_data,
        printer=printer,
        print_=print_,
        poster_url=poster_url or '',
        plugin_names=plugin_names,
    )
