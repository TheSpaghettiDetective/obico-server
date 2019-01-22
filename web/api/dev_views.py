from datetime import datetime, timedelta
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import requests
import json

from app.models import *
from lib.file_storage import save_file_obj
from lib import redis

STATUS_TTL_SECONDS = 60

def command_response(printer):
    commands = PrinterCommand.objects.filter(printer=printer, status=PrinterCommand.PENDING)
    resp = Response({'commands': [ json.loads(c.command) for c in commands ]})
    commands.update(status=PrinterCommand.SENT)
    return resp


class PrinterPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth

        pic = request.data['pic']
        internal_url, external_url = save_file_obj('{}/{}.jpg'.format(printer.id, int(time.time())), pic, request)
        redis.printer_pic_set(printer.id, 'img_url', external_url, ex=STATUS_TTL_SECONDS)

        current_print_filename = redis.printer_status_get(printer.id, 'current_print_filename')
        if not current_print_filename:
            return Response({'result': 'OK'})

        resp = requests.get(settings.ML_HOST + '/p', params={'img': internal_url})
        resp.raise_for_status()

        det = resp.json()
        score = sum([ d[1] for d in det ])
        redis.printer_pic_set(printer.id, 'score', score, ex=STATUS_TTL_SECONDS)

        if score > settings.ALERT_THRESHOLD and not printer.alert_outstanding:
            printer.alert_outstanding = True
            printer.save()
            
            PrinterCommand.objects.create(printer=printer, command=json.dumps({'cmd': 'pause'}), status=PrinterCommand.PENDING)

        print(det)
        print(score)
        return command_response(printer)


class PrinterStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        def file_printing(octoprint_data):
            printing = False
            flags = octoprint_data.get('state', {}).get('flags', {})
            for flag in ('cancelling', 'paused', 'pausing', 'printing', 'resuming', 'finishing'):
                if flags.get(flag, False):
                    printing = True

            file_name = octoprint_data.get('job', {}).get('file', {}).get('name')
            return file_name, printing, octoprint_data.get('state', {}).get('text')

        printer = request.auth

        status = request.data
        file_name, printing, text = file_printing(status.get('octoprint_data', {}))

        redis.printer_status_set(printer.id, 'text', text, ex=STATUS_TTL_SECONDS)
        if printing:
            redis.printer_status_set(printer.id, 'current_print_filename', file_name, ex=STATUS_TTL_SECONDS)
        else:
            redis.printer_status_delete(printer.id, 'current_print_filename')

        return command_response(printer)
