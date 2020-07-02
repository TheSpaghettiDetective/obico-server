from django.utils import timezone
import json

from lib import redis
from lib import channels
from lib.utils import set_as_str_if_present
from app.models import PrintEvent
from app.tasks import service_webhook

STATUS_TTL_SECONDS = 240
SVC_WEBHOOK_EVENTS = ['PrintResumed', 'PrintPaused', 'PrintFailed', 'PrintDone', 'PrintCancelled', 'PrintStarted']
SVC_WEBHOOK_PROGRESS_PCTS = [25, 50, 75]

def process_octoprint_status(printer, status):
    octoprint_settings = status.get('octoprint_settings')
    if octoprint_settings:
        redis.printer_settings_set(printer.id, settings_dict(octoprint_settings))

    octoprint_data = dict()
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'state')
    set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'progress')
    set_as_str_if_present(octoprint_data, status, 'octoprint_temperatures', 'temperatures')
    redis.printer_status_set(printer.id, octoprint_data, ex=STATUS_TTL_SECONDS)

    if status.get('current_print_ts'):
        process_octoprint_status_with_ts(status, printer)

    channels.send_status_to_web(printer.id)


def settings_dict(octoprint_settings):
    settings = dict(('webcam_' + k, str(v)) for k, v in octoprint_settings.get('webcam', {}).items())
    settings.update(dict(temp_profiles=json.dumps(octoprint_settings.get('temperature', {}).get('profiles', []))))
    settings.update(dict(printer_metadata=json.dumps(octoprint_settings.get('printer_metadata', {}))))
    return settings


def process_octoprint_status_with_ts(op_status, printer):
    op_event = op_status.get('octoprint_event', {})
    op_data = op_status.get('octoprint_data', {})
    print_ts = op_status.get('current_print_ts')
    current_filename = op_event.get('name') or op_data.get('job', {}).get('file', {}).get('name')
    if not current_filename:
        return
    printer.update_current_print(current_filename, print_ts)
    if not printer.current_print:
        return

    # Events for external service webhooks such as 3D Geeks
    # This has to happen before event saving, as `current_print` may change after event saving.
    call_service_webhook_if_needed(printer, op_event, op_data)


    if op_event.get('event_type') in ('PrintCancelled', 'PrintFailed'):
        printer.current_print.cancelled_at = timezone.now()
        printer.current_print.save()
    if op_event.get('event_type') in ('PrintFailed', 'PrintDone'):
        printer.unset_current_print()
    if op_event.get('event_type') == 'PrintPaused':
        printer.current_print.paused_at = timezone.now()
        printer.current_print.save()
        PrintEvent.create(printer.current_print, PrintEvent.PAUSED)
    if op_event.get('event_type') == 'PrintResumed':
        printer.current_print.paused_at = None
        printer.current_print.save()
        PrintEvent.create(printer.current_print, PrintEvent.RESUMED)

def call_service_webhook_if_needed(printer, op_event, op_data):
    if not printer.service_token:
        return

    if op_event.get('event_type') in SVC_WEBHOOK_EVENTS:
        service_webhook.delay(printer.current_print.id, op_event.get('event_type'))

    print_time = op_data.get('progress', {}).get('printTime')
    print_time_left = op_data.get('progress', {}).get('printTimeLeft')
    pct = op_data.get('progress', {}).get('completion')
    last_progress = redis.print_progress_get(printer.current_print.id)
    next_progress_pct = next(iter(list(filter(lambda x: x > last_progress, SVC_WEBHOOK_PROGRESS_PCTS))), None)
    if pct and print_time and print_time_left and next_progress_pct and pct >= next_progress_pct:
        redis.print_progress_set(printer.current_print.id, next_progress_pct)
        service_webhook.delay(printer.current_print.id, 'PrintProgress', percent=pct, timeleft=int(print_time_left), currenttime=int(print_time))
