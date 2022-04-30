from django.utils import timezone
import json
from typing import Dict

from lib import cache
from lib import channels
from lib.utils import set_as_str_if_present
from lib import mobile_notifications
from app.models import PrintEvent, Printer
from lib.heater_trackers import process_heater_temps

STATUS_TTL_SECONDS = 240

def process_octoprint_status(printer: Printer, status: Dict) -> None:
    octoprint_settings = status.get('octoprint_settings')
    if octoprint_settings:
        cache.printer_settings_set(printer.id, settings_dict(octoprint_settings))

    # for backward compatibility
    if status.get('octoprint_data'):
        if 'octoprint_temperatures' in status:
            status['octoprint_data']['temperatures'] = status['octoprint_temperatures']

    if not status.get('octoprint_data'):
        cache.printer_status_delete(printer.id)
    elif status.get('octoprint_data', {}).get('_ts'):   # data format for plugin 1.6.0 and higher
        cache.printer_status_set(printer.id, json.dumps(status.get('octoprint_data', {})), ex=STATUS_TTL_SECONDS)
    else:
        octoprint_data: Dict = dict()
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'state')
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'progress')
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'file_metadata')
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'currentZ')
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'job')
        set_as_str_if_present(octoprint_data, status.get('octoprint_data', {}), 'temperatures')
        cache.printer_status_set(printer.id, octoprint_data, ex=STATUS_TTL_SECONDS)

    if status.get('current_print_ts'):
        process_octoprint_status_with_ts(status, printer)

    channels.send_status_to_web(printer.id)

    temps = status.get('octoprint_data', {}).get('temperatures', None)
    if temps:
        process_heater_temps(printer, temps)


def settings_dict(octoprint_settings):
    settings = dict(('webcam_' + k, str(v)) for k, v in octoprint_settings.get('webcam', {}).items())
    settings.update(dict(temp_profiles=json.dumps(octoprint_settings.get('temperature', {}).get('profiles', []))))
    settings.update(dict(printer_metadata=json.dumps(octoprint_settings.get('printer_metadata', {}))))
    settings.update(
        tsd_plugin_version=octoprint_settings.get('tsd_plugin_version', ''),
        octoprint_version=octoprint_settings.get('octoprint_version', ''),
        client_id=octoprint_settings.get('client_id', ''),
        client_version=octoprint_settings.get('client_version', ''),
    )
    settings.update(
        dict(('agent_' + k, str(v)) for k, v in octoprint_settings.get('agent', {}).items())
    )
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

    # Notification for mobile devices
    # This has to happen before event saving, as `current_print` may change after event saving.
    mobile_notifications.send_if_needed(printer.current_print, op_event, op_data)

    if op_event.get('event_type') == 'PrintCancelled':
        printer.current_print.cancelled_at = timezone.now()
        printer.current_print.save()
    elif op_event.get('event_type') == 'PrintFailed':
        # setting cancelled_at here, original commit:
        # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/commit/86d1a18d34a9d895e9d9284d5048e45afa1e56a1
        printer.current_print.cancelled_at = timezone.now()
        printer.current_print.save()
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintDone':
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintPaused':
        printer.current_print.paused_at = timezone.now()
        printer.current_print.save()
        PrintEvent.create(printer.current_print, PrintEvent.PAUSED)
    elif op_event.get('event_type') == 'PrintResumed':
        printer.current_print.paused_at = None
        printer.current_print.save()
        PrintEvent.create(printer.current_print, PrintEvent.RESUMED)
    elif op_event.get('event_type') == 'FilamentChange':
        PrintEvent.create(printer.current_print, PrintEvent.FILAMENT_CHANGE)