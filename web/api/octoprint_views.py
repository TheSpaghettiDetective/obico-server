from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.core import serializers
import requests
import json
import io
from PIL import Image

from lib.file_storage import save_file_obj
from lib import redis
from lib.image import overlay_detections
from app.models import *
from app.notifications import send_failure_alert
from lib.prediction import update_prediction_with_detections, is_failing
from lib.channels import send_commands_to_group, send_status_to_group
from .octoprint_messages import process_octoprint_status, STATUS_TTL_SECONDS

ALERT_COOLDOWN_SECONDS = 120

def alert_if_needed(printer):
    last_acknowledge = printer.alert_acknowledged_at or datetime.fromtimestamp(0, timezone.utc)
    if printer.current_print_alerted_at \
        or (timezone.now() - last_acknowledge).total_seconds() < ALERT_COOLDOWN_SECONDS:
        return

    printer.set_alert()

    pause_print = printer.action_on_failure == Printer.PAUSE
    if pause_print:
        printer.pause_print_on_failure()

    send_failure_alert(printer, pause_print)

def command_response(printer):
    send_commands_to_group(printer.id)
    send_status_to_group(printer.id)
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
        pic_id = int(timezone.now().timestamp())
        internal_url, external_url = save_file_obj('raw/{}/{}.jpg'.format(printer.id, pic_id), pic, settings.PICS_CONTAINER)

        if not printer.is_printing():
            redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=STATUS_TTL_SECONDS)
            return command_response(printer)

        req = requests.get(settings.ML_API_HOST + '/p', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        resp = req.json()

        detections = resp['detections']
        prediction = PrinterPrediction.objects.get(printer=printer)
        update_prediction_with_detections(prediction, detections)
        prediction.save()

        pic.file.seek(0)  # Reset file object pointer so that we can load it again
        tagged_img = io.BytesIO()
        overlay_detections(Image.open(pic), detections).save(tagged_img, "JPEG")
        tagged_img.seek(0)
        _, external_url = save_file_obj('tagged/{}/{}.jpg'.format(printer.id, pic_id), tagged_img, settings.PICS_CONTAINER)
        redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=STATUS_TTL_SECONDS)

        prediction_json = serializers.serialize("json", [prediction, ])
        p_out = io.BytesIO()
        p_out.write(prediction_json.encode('UTF-8'))
        p_out.seek(0)
        save_file_obj('p/{}/{}.json'.format(printer.id, pic_id), p_out, settings.PICS_CONTAINER, return_url=False)

        if is_failing(prediction, printer.detective_sensitivity):
            alert_if_needed(printer)

        return command_response(printer)


class OctoPrintStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        printer = request.auth
        process_octoprint_status(printer, request.data)
        return command_response(printer)
