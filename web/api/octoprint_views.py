from datetime import datetime, timedelta
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
from app.emails import send_failure_alert


STATUS_TTL_SECONDS = 180

def command_response(printer):
    commands = PrinterCommand.objects.filter(printer=printer, status=PrinterCommand.PENDING)
    resp = Response({'commands': [ json.loads(c.command) for c in commands ]})
    commands.update(status=PrinterCommand.SENT)
    return resp


class OctoPrintPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth

        pic = request.data['pic']
        internal_url, external_url = save_file_obj('{}/{}.jpg'.format(printer.id, int(time.time())), pic)
        redis.printer_pic_set(printer.id, 'img_url', external_url, ex=STATUS_TTL_SECONDS)

        if not printer.current_print_filename:
            return command_response(printer)

        resp = requests.get(settings.ML_API_HOST + '/p', params={'img': internal_url})
        resp.raise_for_status()

        det = resp.json()
        score = sum([ d[1] for d in det ])
        redis.printer_pic_set(printer.id, 'score', score, ex=STATUS_TTL_SECONDS)

        if score > settings.ALERT_THRESHOLD and not printer.current_print_alerted_at and not printer.current_print_alert_muted:
            printer.set_alert()
            PrinterCommand.objects.create(printer=printer, command=json.dumps({'cmd': 'pause'}), status=PrinterCommand.PENDING)
            send_failure_alert(printer)

        print(det)
        print(score)
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
