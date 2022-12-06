from django.utils import timezone
import json
from typing import Dict
import logging

from lib import cache
from lib import channels
from lib.utils import set_as_str_if_present
from lib import mobile_notifications
from app.models import PrinterEvent, Printer
from lib.heater_trackers import process_heater_temps

LOGGER = logging.getLogger(__name__)
STATUS_TTL_SECONDS = 240

def process_octoprint_status(printer: Printer, msg: Dict) -> None:
    # Backward compatibility: octoprint_settings is for OctoPrint-Obico 2.1.2 or earlier, or moonraker-obico 0.5.1 or earlier
    octoprint_settings = msg.get('settings') or msg.get('octoprint_settings')
    if octoprint_settings:
        cache.printer_settings_set(printer.id, settings_dict(octoprint_settings))

        agent_name = octoprint_settings.get('agent', {}).get('name')
        agent_version = octoprint_settings.get('agent', {}).get('version')
        if agent_name != printer.agent_name or agent_version != printer.agent_version:
            printer.agent_name = agent_name
            printer.agent_version = agent_version
            printer.save()


    # Backward compatibility: octoprint_data is for OctoPrint-Obico 2.1.2 or earlier, or moonraker-obico 0.5.1 or earlier
    printer_status = msg.get('status') or msg.get('octoprint_data')

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
    settings.update(dict(platform_uname=json.dumps(octoprint_settings.get('platform_uname', []))))

    return settings


def update_current_print_if_needed(msg, printer):
    if not msg.get('current_print_ts'):  # Absence of current_print_ts means OctoPrint/Moonraker has lost the connection to the printer, and hence printing status unknown.
        LOGGER.warn(f'current_print_ts not present. Received status: {msg}')
        return

    # Backward compatibility: octoprint_event is for OctoPrint-Obico 2.1.2 or earlier, or moonraker-obico 0.5.1 or earlier
    op_event = msg.get('event') or msg.get('octoprint_event') or {}
    printer_status = msg.get('status') or msg.get('octoprint_data') or {}

    print_ts = msg.get('current_print_ts')
    g_code_file_id = printer_status.get('job', {}).get('file', {}).get('obico_g_code_file_id') \
        or msg.get('tsd_gcode_file_id')  # tsd_gcode_file_id to be compatible with version 2.2.x and earlier
    current_filename = (op_event.get('data') or {}).get('name') or ((printer_status.get('job') or {}).get('file') or {}).get('name')
    printer.update_current_print(print_ts, g_code_file_id, current_filename)
    if not printer.current_print:
        return

    # Notification for mobile devices
    # This has to happen before event saving, as `current_print` may change after event saving.
    mobile_notifications.send_if_needed(printer.current_print, op_event, printer_status)

    if op_event.get('event_type') == 'PrintCancelled':
        printer.current_print.cancelled()
    elif op_event.get('event_type') == 'PrintFailed':
        # setting cancelled_at here, original commit:
        # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/commit/86d1a18d34a9d895e9d9284d5048e45afa1e56a1
        printer.current_print.cancelled()
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintDone':
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintPaused':
        printer.current_print.paused()
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.PAUSED, task_handler=True)
    elif op_event.get('event_type') == 'PrintResumed':
        printer.current_print.resumed()
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.RESUMED, task_handler=True)
    elif op_event.get('event_type') == 'FilamentChange':
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.FILAMENT_CHANGE, task_handler=True)