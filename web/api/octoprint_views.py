from datetime import datetime, timedelta, timezone
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import requests
import json

from lib.file_storage import save_file_obj
from lib import redis
from app.models import *
from app.notifications import send_failure_alert


STATUS_TTL_SECONDS = 180
ALERT_COOLDOWN_SECONDS = 120

def send_alert_if_needed(printer, p):
    last_acknowledge = printer.alert_acknowledged_at or datetime.fromtimestamp(0, timezone.utc)
    if p < settings.ALERT_P_THRESHOLD \
        or printer.current_print_alerted_at \
        or (datetime.now(timezone.utc) - last_acknowledge).total_seconds() < ALERT_COOLDOWN_SECONDS:
        return

    printer.set_alert()

    pause_print = printer.action_on_failure == Printer.PAUSE
    if pause_print:
        printer.pause_print_on_failure()
    send_failure_alert(printer, pause_print)

def command_response(printer):
    commands = PrinterCommand.objects.filter(printer=printer, status=PrinterCommand.PENDING)
    resp = Response({'commands': [ json.loads(c.command) for c in commands ]})
    commands.update(status=PrinterCommand.SENT)
    return resp

def ml_api_auth_headers():
    return {"Authorization": "Bearer {}".format(settings.ML_API_TOKEN)} if settings.ML_API_TOKEN else {}

class OctoPrintPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth

        pic = request.data['pic']
        internal_url, external_url = save_file_obj('{}/{}.jpg'.format(printer.id, int(time.time())), pic, settings.PICS_CONTAINER)

        if not printer.current_print_filename or not printer.current_print_started_at:
            redis.printer_pic_set(printer.id, {'img_url': external_url, 'p': '0'}, ex=STATUS_TTL_SECONDS)
            return command_response(printer)

        params = {
            'img': internal_url,
            'session_id': "{}|{}".format(printer.id, int(printer.current_print_started_at.timestamp()))
        }

        req = requests.get(settings.ML_API_HOST + '/p', params=params, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        resp = req.json()
        p = resp['p']
        redis.printer_pic_set(printer.id, {'img_url': external_url, 'p': p}, ex=STATUS_TTL_SECONDS)

        print(resp['detections'])
        print(p)

        send_alert_if_needed(printer, p)
        return command_response(printer)


class OctoPrintStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        def file_printing(octoprint_data):
            printing = False
            flags = octoprint_data.get('state', {}).get('flags', {})
            for flag in ('cancelling', 'paused', 'pausing', 'printing', 'resuming', 'finishing'):
                if flags.get(flag, False):
                    printing = True

            filename = octoprint_data.get('job', {}).get('file', {}).get('name')
            return filename, printing, octoprint_data.get('state', {}).get('text')

        printer = request.auth

        status = request.data
        octo_data = status.get('octoprint_data', {})
        filename, printing, text = file_printing(octo_data)
        seconds_left = octo_data.get('progress', {}).get('printTimeLeft') or -1

        redis.printer_status_set(printer.id, {'text': text, 'seconds_left': seconds_left}, ex=STATUS_TTL_SECONDS)
        if printing:
            printer.set_current_print(filename)
        else:
            printer.unset_current_print()

        return command_response(printer)
