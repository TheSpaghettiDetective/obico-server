from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle
from django.conf import settings
from django.core import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
import requests
import json
import io
import os
import logging
from ipware import get_client_ip
from binascii import hexlify

from .utils import report_validationerror
from .printer_discovery import (
    DeviceInfo,
    pull_messages_for_device,
    update_presence_for_device)
from .authentication import PrinterAuthentication
from lib.file_storage import save_file_obj
from lib import cache
from lib.image import overlay_detections
from lib.utils import ml_api_auth_headers
from lib.utils import save_print_snapshot, last_pic_of_print
from app.models import Printer, PrinterPrediction, OneTimeVerificationCode
from notifications.handlers import handler
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.channels import send_status_to_web
from config.celery import celery_app
from .serializers import VerifyCodeInputSerializer, OneTimeVerificationCodeSerializer

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

LOGGER = logging.getLogger(__name__)

IMG_URL_TTL_SECONDS = 60 * 30
ALERT_COOLDOWN_SECONDS = 120


def send_failure_alert(printer: Printer, is_warning: bool, print_paused: bool) -> None:
    LOGGER.info(f'Printer {printer.user.id} {"smells fishy" if is_warning else "is probably failing"}. Sending Alerts')
    if not printer.current_print:
        LOGGER.warn(f'Trying to alert on printer without current print. printer_id: {printer.id}')
        return

    rotated_jpg_url = save_print_snapshot(printer,
                        last_pic_of_print(printer.current_print, 'tagged'),
                        f'snapshots/{printer.id}/{printer.current_print.id}/{str(timezone.now().timestamp())}_rotated.jpg',
                        rotated=True,
                        to_long_term_storage=False)

    handler.send_failure_alerts(
        printer=printer,
        is_warning=is_warning,
        print_paused=print_paused,
        print_=printer.current_print,
        img_url=rotated_jpg_url or ''
    )


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
            pic_path = f'{printer.id}/0.jpg'
        else:
            pic_path = f'{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
        internal_url, external_url = save_file_obj(f'raw/{pic_path}', pic, settings.PICS_CONTAINER, long_term_storage=False)

        if not printer.should_watch() or not printer.actively_printing():
            cache.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)
            send_status_to_web(printer.id)
            return Response({'result': 'ok'})

        req = requests.get(settings.ML_API_HOST + '/p/', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        resp = req.json()

        cache.print_num_predictions_incr(printer.current_print.id)

        detections = resp['detections']
        prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)
        update_prediction_with_detections(prediction, detections)
        prediction.save()

        if prediction.current_p > settings.THRESHOLD_LOW * 0.2:  # Select predictions high enough for focused feedback
            cache.print_high_prediction_add(printer.current_print.id, prediction.current_p, pic_id)

        pic.file.seek(0)  # Reset file object pointer so that we can load it again
        tagged_img = io.BytesIO()
        detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
        overlay_detections(Image.open(pic), detections_to_visualize).save(tagged_img, "JPEG")
        tagged_img.seek(0)

        _, external_url = save_file_obj(f'tagged/{pic_path}', tagged_img, settings.PICS_CONTAINER, long_term_storage=False)
        cache.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)

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


class OctoPrinterView(APIView):
    authentication_classes = (PrinterAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_response(self, printer, user):
        return Response({
            'user': {       # For compatibility with plugin < 1.5.0. Can be removed once old plugins have phased out.
                'is_pro': user.is_pro,
            },
            'printer': {
                'is_pro': user.is_pro,
                'id': printer.id,
                'name': printer.name,
            }
        })

    def get(self, request):
        return self.get_response(request.auth, request.user)

    def patch(self, request):
        Printer.objects.filter(id=request.auth.id).update(**request.data)
        return self.get_response(request.auth, request.user)


# Helper methods

def alert_suppressed(printer):
    if not printer.watching_enabled or printer.current_print is None or printer.current_print.alert_muted_at:
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
        printer.pause_print(initiator='system')
        printer.set_alert()
        send_failure_alert(printer, is_warning=False, print_paused=True)
    elif not last_alerted > last_acknowledged:
        printer.set_alert()
        send_failure_alert(printer, is_warning=False, print_paused=False)


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


class OctoPrinterDiscoveryView(APIView):
    throttle_classes = [AnonRateThrottle]

    @report_validationerror
    def post(self, request, format=None):
        client_ip, is_routable = get_client_ip(request)

        # must guard against possible None or blank value as client_ip
        if not client_ip:
            raise ImproperlyConfigured("cannot determine client_ip")

        device_info: DeviceInfo = DeviceInfo.from_dict(request.data)

        update_presence_for_device(
            client_ip=client_ip,
            device_id=device_info.device_id,
            device_info=device_info,
        )

        messages = pull_messages_for_device(
            client_ip=client_ip,
            device_id=device_info.device_id
        )
        return Response({'messages': [m.asdict() for m in messages]})


class OneTimeVerificationCodeVerifyView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, *args, **kwargs):
        # TODO is kept for backward compatibility
        return self.post(request, *args, **kwargs)

    @report_validationerror
    def post(self, request, *args, **kwargs):
        serializer = VerifyCodeInputSerializer(data={'code': request.GET.get('code')})
        serializer.is_valid(raise_exception=True)

        code = OneTimeVerificationCode.objects.filter(
            code=serializer.validated_data['code']).first()

        if code:
            if not code.printer:
                printer = Printer.objects.create(
                    name="My Awesome Cloud Printer",
                    user=code.user,
                    auth_token=hexlify(os.urandom(10)).decode())
                code.printer = printer
            else:
                # Reset the auth_token for security reason
                code.printer.auth_token = hexlify(os.urandom(10)).decode()
                code.printer.save()

            code.expired_at = timezone.now()
            code.verified_at = timezone.now()
            code.save()
            return Response(OneTimeVerificationCodeSerializer(code, many=False).data)
        else:
            raise Http404("Requested resource does not exist")
