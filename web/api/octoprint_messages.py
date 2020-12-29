from django.utils import timezone
import json
from typing import Dict, Optional, Tuple
import datetime

from lib import cache
from lib import channels
from lib.utils import set_as_str_if_present
from lib import mobile_notifications
from app.models import PrintEvent, Printer, Print, ResurrectionError
from app.tasks import service_webhook
from lib.heater_trackers import process_heater_temps
from django.db import IntegrityError, transaction

STATUS_TTL_SECONDS = 240
SVC_WEBHOOK_PROGRESS_PCTS = [25, 50, 75]

# switch to detected print (without PrintStarted) only
# if current print has no updates since...
# (to ease flapping in case of parallel prints by same token)
CURRENT_SWITCH_OVER_DELTA = datetime.timedelta(seconds=120)

# unset current print if "not printing" for
# (copied old behaviour)
UNSET_DELTA = datetime.timedelta(hours=10)

# update status_at at this interval
# (by default print is touched only if there is state change)
PRINT_TOUCH_DELTA = datetime.timedelta(seconds=90)

# force updating estimate if difference is larger than
# (even if there is no state change)
FORCE_ESTIMATE_DELTA = datetime.timedelta(seconds=600)

# estimated_finished_at cannot be more far ahead than
# (in worst case Printevent.GONE will be emitted around last status_at + this)
MAX_ESTIMATE_DELTA = datetime.timedelta(days=7)


def process_octoprint_status(printer: Printer, status: Dict) -> None:
    octoprint_settings = status.get('octoprint_settings')
    if octoprint_settings:
        cache.printer_settings_set(printer.id, settings_dict(octoprint_settings))

    octoprint_data: Dict = dict()
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'state')
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'progress')
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'file_metadata')
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'currentZ')
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'job')
    set_as_str_if_present(octoprint_data, status, 'octoprint_temperatures', 'temperatures')
    cache.printer_status_set(printer.id, octoprint_data, ex=STATUS_TTL_SECONDS)

    process_octoprint_status_with_ts(status, printer)

    channels.send_status_to_web(printer.id)

    temps = status.get('octoprint_temperatures', None)
    if temps:
        process_heater_temps(printer, temps)


def settings_dict(octoprint_settings):
    settings = dict(('webcam_' + k, str(v)) for k, v in octoprint_settings.get('webcam', {}).items())
    settings.update(dict(temp_profiles=json.dumps(octoprint_settings.get('temperature', {}).get('profiles', []))))
    settings.update(dict(printer_metadata=json.dumps(octoprint_settings.get('printer_metadata', {}))))
    return settings


def process_octoprint_status_with_ts(op_status: Dict, printer: Printer, now: Optional[datetime.datetime] = None) -> None:
    now = timezone.now() if now is None else now
    op_event = op_status.get('octoprint_event', {})
    op_data = op_status.get('octoprint_data', {})
    ext_id = op_status.get('current_print_ts')
    filename = (
        op_event.get('name', '') or
        op_data.get('job', {}).get('file', {}).get('name', '')
    ).strip()

    if ext_id is None or ext_id == -1:
        unset_print_if_untouched(printer, now)
        return

    if not filename:
        raise Exception('current_print_ts is set while filename is missing')

    event_type = op_event.get('event_type', '')
    (print, cevent, pevent) = process_print_event(
        printer, event_type, ext_id, filename, op_status, now)

    # TODO notifications should be based on cevent+pevent+event_type
    # what should it send in case of DETECTED (cevent)?
    # what should happen if its GONE (happens in celery job)?
    # ...

    mobile_notifications.send_if_needed(print, op_event, op_data)
    call_service_webhook_if_needed(printer, print, op_event, op_data)


def process_print_event(printer: Printer,
                        event_type: str,
                        ext_id: int,
                        filename: str,
                        op_status: Dict,
                        now: Optional[datetime.datetime] = None) -> Tuple[Print, Optional[PrintEvent], Optional[PrintEvent]]:
    print: Optional[Print] = None
    cevent: Optional[PrintEvent] = None
    pevent: Optional[PrintEvent] = None
    now = now or timezone.now()

    if event_type == 'PrintStarted':
        (print, pevent) = on_PrintStarted(printer, ext_id, filename, op_status, now)
    else:
        (print, cevent) = get_or_create_print(
            printer, ext_id, filename, op_status, now)

        if event_type == 'PrintCancelled':
            (print, pevent) = on_PrintCancelled(printer, print, now)
        elif event_type == 'PrintFailed':
            (print, pevent) = on_PrintFailed(printer, print, now)
        elif event_type == 'PrintDone':
            (print, pevent) = on_PrintDone(printer, print, now)
        elif event_type == 'PrintPaused':
            (print, pevent) = on_PrintPaused(printer, print, now)
        elif event_type == 'PrintResumed':
            (print, pevent) = on_PrintResumed(printer, print, op_status, now)
        elif print.ended_at() is None:
            # touching print and updating estimate
            save = False

            # lets touch db less often
            delta = now - (print.status_at or print.updated_at)
            if delta > PRINT_TOUCH_DELTA:
                save = True

            next_estimate = extract_estimate(now, op_status)
            if next_estimate is not None:
                if (print.estimated_finished_at is None) or abs(next_estimate - print.estimated_finished_at) > FORCE_ESTIMATE_DELTA:
                    # been empty or difference is too large
                    save = True

            if save:
                print.status_at = now
                if next_estimate is not None:
                    print.estimated_finished_at = next_estimate
                print.save()

    return (print, cevent, pevent)


def extract_estimate(now: datetime.datetime, op_status: Dict) -> Optional[datetime.datetime]:
    remaining: Optional[int] = op_status['octoprint_data'].get('progress', {}).get('printTimeLeft', None)
    if remaining is not None:
        return now + min(
            MAX_ESTIMATE_DELTA,
            datetime.timedelta(seconds=remaining)
        )
    return None


Result = Tuple[Print, Optional[PrintEvent]]


def on_PrintStarted(printer: Printer,
                    ext_id: int,
                    filename: str,
                    op_status: Dict,
                    now: datetime.datetime) -> Result:
    next_estimate = extract_estimate(now, op_status)
    try:
        with transaction.atomic():
            print = Print.objects.create(
                user=printer.user,
                printer=printer,
                ext_id=ext_id,
                filename=filename.strip(),
                started_at=now,
                status_at=now,
                estimated_finished_at=next_estimate,
            )

            # explicit start, set it as current always
            printer.current_print = print
            printer.save()

            printer.printerprediction.reset_for_new_print()
    except IntegrityError:
        raise ResurrectionError(
            'New print does not have unique ext_id? '
            'printer_id: {} | print_ts: {} | filename: {}'.format(
                printer.id, ext_id, filename)
        )

    pevent = PrintEvent.create(print, PrintEvent.STARTED)

    printer.send_should_watch_status()
    assert print  # pleasing mypy
    return (print, pevent)


def on_PrintFailed(printer: Printer, print: Print, now: datetime.datetime) -> Result:
    send_should_watch_status: bool = False
    with transaction.atomic():
        print.cancelled_at = now
        print.status_at = now
        print.save()

        printer.refresh_from_db()
        if print.id == printer.current_print_id:
            printer.current_print = None
            printer.save()

            printer.printerprediction.reset_for_new_print()
            send_should_watch_status = True

    pevent = PrintEvent.create(print, PrintEvent.ENDED)

    if send_should_watch_status:
        printer.send_should_watch_status()

    return (print, pevent)


def on_PrintDone(printer: Printer, print: Print, now: datetime.datetime) -> Result:
    send_should_watch_status: bool = False
    with transaction.atomic():
        print.finished_at = now
        print.status_at = now
        print.save()

        printer.refresh_from_db()
        if print.id == printer.current_print_id:
            printer.current_print = None
            printer.save()

            printer.printerprediction.reset_for_new_print()
            send_should_watch_status = True

    pevent = PrintEvent.create(print, PrintEvent.ENDED)

    if send_should_watch_status:
        printer.send_should_watch_status()

    return (print, pevent)


def on_PrintGone(printer: Optional[Printer], print: Print, now: datetime.datetime) -> Result:
    # !! non-octoprint event !!
    # triggered from celery job what closes
    # forgotten (==untouched) prints
    # (Print.printer is null=True so its optional)

    send_should_watch_status: bool = False
    with transaction.atomic():
        print.cancelled_at = now
        print.gone_at = now
        print.save()

        if printer:
            printer.refresh_from_db()
            if print.id == printer.current_print_id:
                printer.current_print = None
                printer.save()

                printer.printerprediction.reset_for_new_print()
                send_should_watch_status = True

    pevent = PrintEvent.create(print, PrintEvent.GONE)

    if printer and send_should_watch_status:
        printer.send_should_watch_status()

    return (print, pevent)


def on_PrintCancelled(printer: Printer, print: Print, now: datetime.datetime) -> Result:
    print.cancelled_at = now
    print.status_at = now
    print.save()

    # no event for this
    return (print, None)


def on_PrintPaused(printer: Printer, print: Print, now: datetime.datetime) -> Result:
    print.paused_at = now
    print.status_at = now
    print.save()

    pevent = PrintEvent.create(print, PrintEvent.PAUSED)
    return (print, pevent)


def on_PrintResumed(printer: Printer, print: Print, op_status: Dict, now: datetime.datetime) -> Result:
    print.paused_at = None
    print.status_at = now
    print.estimated_finished_at = extract_estimate(now, op_status)
    print.save()

    pevent = PrintEvent.create(print, PrintEvent.RESUMED)
    return (print, pevent)


def get_or_create_print(printer: Printer,
                        ext_id: int,
                        filename: str,
                        op_status: Dict,
                        now: datetime.datetime) -> Result:
    send_should_watch_status = False

    if printer.current_print:
        if printer.current_print.ext_id == ext_id:
            print = printer.current_print
            return (print, None)

    # an ongoing non-current print
    pevent: Optional[PrintEvent] = None
    try:
        next_estimate = extract_estimate(now, op_status)
        with transaction.atomic():
            print, created = Print.objects.get_or_create(
                user=printer.user,
                printer=printer,
                ext_id=ext_id,
                defaults=dict(
                    filename=filename.strip(),
                    started_at=now,
                    status_at=now,
                    estimated_finished_at=next_estimate,
                )
            )

            set_as_current = (
                # when its unset or no changes for current print for a while
                printer.current_print is None or
                (
                    (now - (printer.current_print.status_at or printer.current_print.updated_at)) >
                    CURRENT_SWITCH_OVER_DELTA
                )
            ) and (print.ended_at() is None)

            if set_as_current:
                printer.current_print = print
                printer.save()

                printer.printerprediction.reset_for_new_print()
                send_should_watch_status = True

    except (Print.DoesNotExist, IntegrityError):
        raise ResurrectionError(
            'Current print is deleted! '
            'printer_id: {} | print_ts: {} | filename: {}'.format(
                printer.id, ext_id, filename)
        )

    if created:
        # server has missed PrintStarted
        pevent = PrintEvent.create(print, PrintEvent.DETECTED)

    if send_should_watch_status:
        printer.send_should_watch_status()

    return (print, pevent)


def unset_print_if_untouched(printer: Printer,
                             now: datetime.datetime) -> None:
    unset_cond = (
        printer.current_print is not None and
        (now - (printer.current_print.status_at or printer.current_print.updated_at)) >
        UNSET_DELTA
    )

    if unset_cond:
        with transaction.atomic():
            printer.current_print = None
            printer.save()

            printer.printerprediction.reset_for_new_print()

        printer.send_should_watch_status()


def call_service_webhook_if_needed(printer, print, op_event, op_data):
    if not printer.service_token:
        return

    if op_event.get('event_type') in mobile_notifications.PRINT_EVENTS:
        service_webhook.delay(print.id, op_event.get('event_type'))

    print_time = op_data.get('progress', {}).get('printTime')
    print_time_left = op_data.get('progress', {}).get('printTimeLeft')
    pct = op_data.get('progress', {}).get('completion')
    last_progress = cache.print_progress_get(print.id)
    next_progress_pct = next(iter(list(filter(lambda x: x > last_progress, SVC_WEBHOOK_PROGRESS_PCTS))), None)
    if pct and print_time and print_time_left and next_progress_pct and pct >= next_progress_pct:
        cache.print_progress_set(print.id, next_progress_pct)
        service_webhook.delay(print.id, 'PrintProgress', percent=pct, timeleft=int(print_time_left), currenttime=int(print_time))
