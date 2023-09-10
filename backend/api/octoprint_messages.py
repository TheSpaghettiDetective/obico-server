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
STATUS_TTL_SECONDS = 120

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
    else: # TODO: retire this part after 7/1/2023
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
    webcam_settings = dict(Printer.DEFAULT_WEBCAM_SETTINGS)

    webcam_settings.update(octoprint_settings.get('webcam', {}))
    settings = dict(('webcam_' + k, str(v)) for k, v in webcam_settings.items())

    settings.update(dict(temp_profiles=json.dumps(octoprint_settings.get('temperature', {}).get('profiles', []))))
    settings.update(dict(printer_metadata=json.dumps(octoprint_settings.get('printer_metadata', {}))))
    settings.update(
        tsd_plugin_version=octoprint_settings.get('tsd_plugin_version', ''),
        octoprint_version=octoprint_settings.get('octoprint_version', ''),
    )
    settings.update(dict(platform_uname=json.dumps(octoprint_settings.get('platform_uname', []))))
    settings.update(dict(installed_plugins=json.dumps(octoprint_settings.get('installed_plugins', []))))

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

    if op_event.get('event_type') == 'PrintCancelling':
        # progress data will be reset after PrintCancelling in OctoPrint. Set it now or never.
        update_print_stats_if_needed(printer_status, printer.current_print)
    if op_event.get('event_type') == 'PrintCancelled':
        update_print_stats_if_needed(printer_status, printer.current_print)
        printer.current_print.cancelled()
    elif op_event.get('event_type') == 'PrintFailed':
        # setting cancelled_at here, original commit:
        # https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/commit/86d1a18d34a9d895e9d9284d5048e45afa1e56a1
        printer.current_print.cancelled()
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintDone':
        update_print_stats_if_needed(printer_status, printer.current_print)
        printer.unset_current_print()
    elif op_event.get('event_type') == 'PrintPaused':
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.PAUSED, task_handler=True)
    elif op_event.get('event_type') == 'PrintResumed':
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.RESUMED, task_handler=True)
    elif op_event.get('event_type') == 'FilamentChange':
        PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.FILAMENT_CHANGE, task_handler=True)

def update_print_stats_if_needed(printer_status, _print):
    '''
    This method is idempotent and set the stats at the first chance.
    This is because various versions of OctoPrint-Obico and moonraker-obico
    are not consistent at when the relevant values will be reset.
    For instance, the earliest and the latest events for OctoPrint-Obico are:
    PrintDone, PrintCancelling.
    For moonraker-obico, it's Cancelled, Done, but not with a wrong completion value
    '''
    print_obj_dirty = False

    if _print.print_time is None:

        print_time = printer_status.get('progress', {}).get('printTime')
        if print_time is not None:
            _print.print_time = print_time
        else:
            _print.print_time = (timezone.now() - _print.started_at).total_seconds()

        print_obj_dirty = True

    if _print.filament_used is None:

        completion = printer_status.get('progress', {}).get('completion')
        filament_used = printer_status.get('progress', {}).get('filamentUsed')
        if filament_used is None: #Try Octoprint api
            for key in printer_status.get('job', {}).get('filament'):
                tool_used =  printer_status.get('job', {}).get('filament').get(key).get('length')
                if tool_used is not None:
                    filament_used = (filament_used or 0) + tool_used

        if filament_used is None and completion is not None and _print.g_code_file and _print.g_code_file.filament_total:
            if completion == 0 and print_time and _print.g_code_file.estimated_time: # Old moonraker-obico version sends completion: 0.0 when print ends. We estimate it using print time
                completion = print_time / _print.g_code_file.estimated_time
            filament_used = _print.g_code_file.filament_total * completion / 100.0

        if filament_used is not None:
            _print.filament_used = filament_used
            print_obj_dirty = True

    if print_obj_dirty:
        _print.save()
