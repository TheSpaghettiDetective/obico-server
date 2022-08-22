from django.utils import timezone
import json
from typing import Dict
import logging

from lib import cache
from lib import channels
from lib.utils import set_as_str_if_present
from lib import mobile_notifications
from app.models import PrintEvent, Printer
from lib.heater_trackers import process_heater_temps

LOGGER = logging.getLogger(__name__)
STATUS_TTL_SECONDS = 240

def process_octoprint_status(printer: Printer, msg: Dict) -> None:
    #
    octoprint_settings = msg.get('settings') or msg.get('octoprint_settings')
    if octoprint_settings:
        cache.printer_settings_set(printer.id, settings_dict(octoprint_settings))

    printer_status = msg.get('status') or msg.get('octoprint_data')

    # for backward compatibility
    if printer_status:
        if 'octoprint_temperatures' in msg:
            printer_status['temperatures'] = msg['octoprint_temperatures']

    if not printer_status:
        cache.printer_status_delete(printer.id)
    elif (printer_status or {}).get('_ts'):   # data format for plugin 1.6.0 and higher
        cache.printer_status_set(printer.id, json.dumps((printer_status or {})), ex=STATUS_TTL_SECONDS)
    else:
        octoprint_data: Dict = dict()
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'state')
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'progress')
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'file_metadata')
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'currentZ')
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'job')
        set_as_str_if_present(octoprint_data, (printer_status or {}), 'temperatures')
        cache.printer_status_set(printer.id, octoprint_data, ex=STATUS_TTL_SECONDS)

    update_current_print_if_needed(msg, printer)

    channels.send_status_to_web(printer.id)

    temps = (printer_status or {}).get('temperatures', None)
    if temps:
        process_heater_temps(printer, temps)


def settings_dict(octoprint_settings):
    settings = dict(('webcam_' + k, str(v)) for k, v in octoprint_settings.get('webcam', {}).items())
    settings.update(dict(temp_profiles=json.dumps(octoprint_settings.get('temperature', {}).get('profiles', []))))
    settings.update(dict(printer_metadata=json.dumps(octoprint_settings.get('printer_metadata', {}))))
    settings.update(
        tsd_plugin_version=octoprint_settings.get('tsd_plugin_version', ''),
        octoprint_version=octoprint_settings.get('octoprint_version', ''),
    )
    settings.update(
        dict(('agent_' + k, str(v)) for k, v in octoprint_settings.get('agent', {}).items())
    )
    settings.update(dict(platform_uname=json.dumps(octoprint_settings.get('platform_uname', []))))
    return settings


def update_current_print_if_needed(msg, printer):
    if not msg.get('current_print_ts'):  # Absence of current_print_ts means OctoPrint/Moonraker has lost the connection to the printer, and hence printing status unknown.
        LOGGER.warn(f'current_print_ts not present. Received status: {msg}')
        return

    op_event = msg.get('event') or msg.get('octoprint_event') or {}
    printer_status = msg.get('status') or msg.get('octoprint_data') or {}
    print_ts = msg.get('current_print_ts')
    current_filename = op_event.get('name') or printer_status.get('job', {}).get('file', {}).get('name')
    printer.update_current_print(print_ts, current_filename)
    if not printer.current_print:
        return

    # Notification for mobile devices
    # This has to happen before event saving, as `current_print` may change after event saving.
    mobile_notifications.send_if_needed(printer.current_print, op_event, printer_status)

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