from typing import Dict, Optional, Tuple
import logging

from app.models import Printer, Print, NotificationSetting

from celery import shared_task  # type: ignore

from . import handlers
from .handlers import feature_for_event, notification_plugin_names


LOGGER = logging.getLogger(__name__)


def queue_send_printer_notifications_task(
    event_name: str,
    event_data: dict,
    printer: Printer,
    print_: Optional[Print],
    poster_url: str = '',
) -> None:
    feature = feature_for_event(event_name, event_data)
    if not feature:
        return

    should_fire = NotificationSetting.objects.filter(
        user_id=printer.user_id,
        enabled=True,
        name__in=notification_plugin_names(),
        **{feature.name: True},

    ).exists()

    if should_fire:
        send_printer_notifications.apply_async(
            kwargs={
                'printer_id': printer.id,
                'event_name': event_name,
                'event_data': event_data,
                'print_id': print_.id if print_ else None,
                'poster_url': poster_url,
            }
        )


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
    printer = Printer.objects.select_related('user').get(id=printer_id)  # FIXME any additional filter? User.is_active?
    print_ = Print.objects.get(id=print_id) if print_id else None
    handlers.send_printer_notifications(
        event_name=event_name,
        event_data=event_data,
        printer=printer,
        print_=print_,
        poster_url=poster_url or '',
        plugin_names=plugin_names,
    )
