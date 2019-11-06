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
from lib.utils import ml_api_auth_headers
from app.models import *
from app.notifications import send_failure_alert
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.channels import send_commands_to_printer, send_status_to_web
from .octoprint_messages import STATUS_TTL_SECONDS
from config.celery import celery_app

ALERT_COOLDOWN_SECONDS = 120

def alert_suppressed(printer):
    if printer.current_print == None:
        return True

    last_acknowledged = printer.current_print.alert_acknowledged_at or datetime.fromtimestamp(0, timezone.utc)
    return (timezone.now() - last_acknowledged).total_seconds() < ALERT_COOLDOWN_SECONDS

def alert_if_needed(printer):
    if alert_suppressed(printer):
        return

    last_acknowledged = printer.current_print.alert_acknowledged_at or datetime.fromtimestamp(1, timezone.utc)
    last_alerted = printer.current_print.alerted_at or datetime.fromtimestamp(0, timezone.utc)
    if last_alerted > last_acknowledged:
        return

    printer.set_alert()
    send_failure_alert(printer, is_warning=True, print_paused=False)

def pause_if_needed(printer):
    if alert_suppressed(printer):
        return

    last_acknowledged = printer.current_print.alert_acknowledged_at or datetime.fromtimestamp(1, timezone.utc)
    last_alerted = printer.current_print.alerted_at or datetime.fromtimestamp(0, timezone.utc)

    if printer.action_on_failure == Printer.PAUSE and not printer.current_print.paused_at:
        printer.pause_print()
        printer.set_alert()
        send_failure_alert(printer, is_warning=False, print_paused=True)
    elif not last_alerted > last_acknowledged:
        printer.set_alert()
        send_failure_alert(printer, is_warning=False, print_paused=False)

def command_response(printer):
    send_commands_to_printer(printer.id)
    send_status_to_web(printer.id)
    commands = PrinterCommand.objects.filter(printer=printer, status=PrinterCommand.PENDING)
    resp = Response({'commands': [ json.loads(c.command) for c in commands ]})
    commands.update(status=PrinterCommand.SENT)
    return resp

class OctoPrintPicView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth

        pic = request.FILES['pic']
        pic_id = int(timezone.now().timestamp())
        internal_url, external_url = save_file_obj('raw/{}/{}.jpg'.format(printer.id, pic_id), pic, settings.PICS_CONTAINER)

        if not printer.should_watch():
            redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=STATUS_TTL_SECONDS)
            return command_response(printer)

        req = requests.get(settings.ML_API_HOST + '/p/', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        resp = req.json()

        detections = resp['detections']
        prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)
        update_prediction_with_detections(prediction, detections)
        prediction.save()

        pic.file.seek(0)  # Reset file object pointer so that we can load it again
        tagged_img = io.BytesIO()
        detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
        overlay_detections(Image.open(pic), detections_to_visualize).save(tagged_img, "JPEG")
        tagged_img.seek(0)
        _, external_url = save_file_obj('tagged/{}/{}.jpg'.format(printer.id, pic_id), tagged_img, settings.PICS_CONTAINER)
        redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=STATUS_TTL_SECONDS)

        prediction_json = serializers.serialize("json", [prediction, ])
        redis.printer_p_json_set(printer.id, pic_id, prediction_json, ex=60*60*24*2)

        if is_failing(prediction, printer.detective_sensitivity, escalating_factor=settings.ESCALATING_FACTOR):
            pause_if_needed(printer)
        elif is_failing(prediction, printer.detective_sensitivity, escalating_factor=1):
            alert_if_needed(printer)

        redis.print_num_predictions_incr(printer.current_print.id)
        return command_response(printer)


class OctoPrintPingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'status': 'pong'})
