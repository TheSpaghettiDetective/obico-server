from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import requests

from app.models import *
from .file_storage import save_file_obj


class PrinterPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth

        pic = request.data['pic']
        internal_url, external_url = save_file_obj('{}/1.jpg'.format(printer.id), pic, request)
        printer.current_img_url = external_url
        printer.last_contacted = datetime.now()
        printer.save()

        existing_print = Print.objects.filter(printer=printer, ended_at__isnull=True).first()
        if not existing_print:
            return Response({'result': 'OK'})
        
        resp = requests.get(settings.ML_HOST + '/p', params={'img': internal_url})
        resp.raise_for_status()

        det = resp.json()
        score = sum([ d[1] for d in det ])

        printer.detection_score = score
        printer.save()

        print(det)
        print(score)
        return Response({'result': det})


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
            return file_name, printing

        printer = request.auth
        printer.last_contacted = datetime.now()
        printer.save()
        
        status = request.data
        file_name, printing = file_printing(status.get('octoprint_data', {}))
        existing_print = Print.objects.filter(printer=printer, ended_at__isnull=True).first()

        if not printing:
            if existing_print:
                existing_print.ended_at = datetime.now()
        else:
            if not existing_print:
                existing_print = Print(name=file_name, printer=printer, started_at=datetime.now())
            elif existing_print.name != file_name:
                existing_print.ended_at = datetime.now()
                existing_print.save()
                existing_print = Print(name=file_name, printer=printer, started_at=datetime.now())

        if existing_print:
            existing_print.save()

        return Response({'result': 'OK'})