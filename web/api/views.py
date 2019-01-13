from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import requests
from azure.storage.blob import BlockBlobService, BlobPermissions

from app.models import *


class PrinterPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request._auth

        existing_print = Print.objects.filter(printer=printer, finished_at__isnull=True).first()
        if not existing_print:
            return Response({'result': 'OK'})

        pic = request.data['pic'].file

        blob_service = BlockBlobService(
            account_name=settings.AZURE_STORAGE_ACCOUNT,
            account_key=settings.AZURE_STORAGE_KEY)

        container = settings.AZURE_STORAGE_CONTAINER
        obj_name = '{}/1.jpg'.format(printer.id)
        blob_service.create_blob_from_stream(container, obj_name, pic)
        sas_token = blob_service.generate_blob_shared_access_signature(container,'1.jpg',BlobPermissions.READ,datetime.utcnow() + timedelta(hours=24*3000))
        blob_url = blob_service.make_blob_url(container, obj_name, sas_token=sas_token)
        resp = requests.get('http://ml_api:3333/p', params={'img': blob_url})
        resp.raise_for_status()

        det = resp.json()
        score = sum([ d[1] for d in det ])

        existing_print.detection_score = score
        existing_print.current_img_url= blob_url
        existing_print.current_img_num += 1
        existing_print.save()

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

        printer = request._auth
        status = request.data
        file_name, printing = file_printing(status.get('octoprint_data', {}))

        existing_print = Print.objects.filter(printer=printer, finished_at__isnull=True).first()

        if existing_print and existing_print.name != file_name:
            existing_print.finished_at = datetime.now()
        
        if printing and not existing_print:
            existing_print = Print(name=file_name, printer=printer, current_img_num=0)
        
        if existing_print:
            existing_print.save()

        return Response({'result': 'OK'})