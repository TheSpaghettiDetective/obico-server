import logging
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.core import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
import requests
import json
import io
from PIL import Image

from .authentication import PrinterAuthentication
from lib.file_storage import save_file_obj
from lib import redis
from lib.image import overlay_detections
from lib.utils import ml_api_auth_headers
from app.models import *
from app.notifications import send_failure_alert
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.channels import send_status_to_web
from config.celery import celery_app

IMG_URL_TTL_SECONDS = 60 * 30
ALERT_COOLDOWN_SECONDS = 120

LOGGER = logging.getLogger(__name__)


def alert_suppressed(printer):
    if not printer.watching or printer.current_print is None or printer.current_print.alert_muted_at:
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


class OctoPrintPicView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (PrinterAuthentication,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth
        printer.refresh_from_db()  # Connection is keep-alive, which means printer object can be stale.

        pic = request.FILES['pic']
        pic = cap_image_size(pic)
        pic_id = str(timezone.now().timestamp())

        if not printer.current_print:     # Some times pics come in when current_print is not set - maybe because printer status is out of sync between plugin and server?
            pic_path = f'{printer.id}/0/{pic_id}.jpg'
        else:
            pic_path = f'{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
        internal_url, external_url = save_file_obj(f'raw/{pic_path}', pic, settings.PICS_CONTAINER, long_term_storage=False)

        if not printer.should_watch() or not printer.actively_printing():
            redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)
            send_status_to_web(printer.id)
            return Response({'result': 'ok'})

        req = requests.get(settings.ML_API_HOST + '/p/', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        resp = req.json()

        redis.print_num_predictions_incr(printer.current_print.id)

        detections = resp['detections']
        prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)
        update_prediction_with_detections(prediction, detections)
        prediction.save()

        if prediction.current_p > settings.THRESHOLD_LOW * 0.2:  # Select predictions high enough for focused feedback
            redis.print_high_prediction_add(printer.current_print.id, prediction.current_p, pic_id)

        pic.file.seek(0)  # Reset file object pointer so that we can load it again
        tagged_img = io.BytesIO()
        detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
        overlay_detections(Image.open(pic), detections_to_visualize).save(tagged_img, "JPEG")
        tagged_img.seek(0)

        _, external_url = save_file_obj(f'tagged/{pic_path}', tagged_img, settings.PICS_CONTAINER, long_term_storage=False)
        redis.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)

        prediction_json = serializers.serialize("json", [prediction, ])
        p_out = io.BytesIO()
        p_out.write(prediction_json.encode('UTF-8'))
        p_out.seek(0)
        save_file_obj(f'p/{printer.id}/{printer.current_print.id}/{pic_id}.json', p_out, settings.PICS_CONTAINER, long_term_storage=False)

        if is_failing(prediction, printer.detective_sensitivity, escalating_factor=settings.ESCALATING_FACTOR):
            pause_if_needed(printer)
        elif is_failing(prediction, printer.detective_sensitivity, escalating_factor=1):
            alert_if_needed(printer)

        send_status_to_web(printer.id)
        return Response({'result': 'ok'})


class OctoPrintPingView(APIView):
    authentication_classes = (PrinterAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({
            'user': {
                'is_pro': user.is_pro,
            }
        })


def cap_image_size(pic):
    im = Image.open(pic.file)
    if max(im.size) <= 1296:
        pic.file.seek(0)
        return pic

    im.thumbnail((1280, 960), Image.ANTIALIAS)
    output = io.BytesIO()
    im.save(output, format='JPEG')
    output.seek(0)
    return InMemoryUploadedFile(
        output,
        u"pic",
        'pic',
        pic.content_type,
        len(output.getbuffer()),
        None)
