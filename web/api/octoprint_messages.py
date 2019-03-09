from django.utils import timezone

from lib import redis
from lib import channels

STATUS_TTL_SECONDS = 240

def process_octoprint_status(printer, status):

    def file_printing(op_status, printer):
        # Event, if present, should be used to determine the printing status
        op_event = op_status.get('octoprint_event', {})
        filename = (op_event.get('data') or {}).get('name')    # octoprint_event may be {'data': null, xxx}
        if filename and op_event.get('event_type') == 'PrintStarted':
            return filename, True, False
        if filename and op_event.get('event_type') == 'PrintDone':
            return filename, False, False
        if filename and op_event.get('event_type') == 'PrintCancelled':
            return filename, False, True

        # No event. Fall back to using octoprint_data.
        # But we wait for a period because octoprint_data can be out of sync with octoprint_event briefly and cause race condition
        if (timezone.now() - printer.print_status_updated_at).total_seconds() < 60:
            return None, None, None

        octoprint_data = op_status.get('octoprint_data', {})
        filename = octoprint_data.get('job', {}).get('file', {}).get('name')
        printing = False
        flags = octoprint_data.get('state', {}).get('flags', {})
        for flag in ('cancelling', 'paused', 'pausing', 'printing', 'resuming', 'finishing'):
            if flags.get(flag, False):
                printing = True

        return filename, printing, False   # we can't derive from octoprint_data if the job was cancelled. Always return true.

    def settings_dict(octoprint_settings):
        return dict(('webcam_'+k, str(v)) for k, v in octoprint_settings['webcam'].items())

    octoprint_settings = status.get('octoprint_settings')
    if octoprint_settings:
        redis.printer_settings_set(printer.id, settings_dict(octoprint_settings))

    octoprint_data = status.get('octoprint_data', {})
    seconds_left = octoprint_data.get('progress', {}).get('printTimeLeft') or -1
    redis.printer_status_set(printer.id, {'text': octoprint_data.get('state', {}).get('text'), 'seconds_left': seconds_left}, ex=STATUS_TTL_SECONDS)

    filename, printing, cancelled = file_printing(status, printer)
    if printing is not None:
        if printing:
            printer.set_current_print(filename)
        else:
            printer.unset_current_print(cancelled)

    channels.send_status_to_group(printer.id)
