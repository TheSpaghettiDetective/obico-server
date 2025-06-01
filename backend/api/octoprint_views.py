from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import time
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework import viewsets, mixins
from rest_framework import status
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
from python_ipware import IpWare
from ipware import get_client_ip
from binascii import hexlify

from .utils import report_validationerror
from lib.printer_discovery import (
    pull_messages_for_device,
    update_presence_for_device,)
from lib.one_time_passcode import request_one_time_passcode
from .authentication import PrinterAuthentication
from lib.file_storage import save_file_obj
from lib import cache
from lib.image import overlay_detections
from lib.utils import ml_api_auth_headers
from lib.utils import save_pic, get_rotated_pic_url
from app.models import Printer, PrinterPrediction, OneTimeVerificationCode, PrinterEvent, GCodeFile
from notifications.handlers import handler
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.channels import send_status_to_web
from config.celery import celery_app
from .serializers import VerifyCodeInputSerializer, OneTimeVerificationCodeSerializer, GCodeFileSerializer
from PIL import Image, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True

LOGGER = logging.getLogger(__name__)

IMG_URL_TTL_SECONDS = 60 * 30
ALERT_COOLDOWN_SECONDS = 90


def send_failure_alert(printer: Printer, img_url, is_warning: bool, print_paused: bool) -> None:
    if not printer.current_print:
        LOGGER.warn(f'Trying to alert on printer without current print. printer_id: {printer.id}')
        return

    # TODO: I am pretty sure this can be DRYed by consolidating FAILURE_ALERTED with how other printer events are handled.
    PrinterEvent.create(print=printer.current_print, event_type=PrinterEvent.FAILURE_ALERTED, task_handler=False)

    rotated_jpg_url = get_rotated_pic_url(printer, img_url, force_snapshot=True)

    handler.queue_send_failure_alerts_task(
        print_id=printer.current_print_id,
        is_warning=is_warning,
        print_paused=print_paused,
        img_url=rotated_jpg_url or '',
    )


class OctoPrintPicView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (PrinterAuthentication,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        printer = request.auth
        user = request.user

        try:
            printer.refresh_from_db()  # Connection is keep-alive, which means printer object can be stale.
        except Printer.DoesNotExist:
            # refresh_from_db() may throw DoesNotExist if the printer has been deleted. https://sentry.obico.io/organizations/sentry/issues/19101/?project=8&project=9&project=4&project=2&query=is%3Aunresolved&referrer=issue-stream&sort=new&statsPeriod=90d
            return Response(status=status.HTTP_404_NOT_FOUND)

        is_primary_camera = request.POST.get('is_primary_camera', 'true').lower() == 'true' # if not specified, it's from a legacy agent and hence is primary camera
        is_nozzle_camera = request.POST.get('is_nozzle_camera', 'false').lower() == 'true'
        camera_name = request.POST.get('camera_name', '') # If camera_name is not provided, it's from a legacy agent.

        # TODO: Think about the use cases when non-primary camera sends a pic. For now, we are ignoring it.
        if not is_primary_camera:
            return Response({'result': 'ok'})

        if settings.PIC_POST_LIMIT_PER_MINUTE and cache.pic_post_over_limit(printer.id, settings.PIC_POST_LIMIT_PER_MINUTE):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        if not request.FILES.get('pic'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pic = request.FILES['pic']
        pic = cap_image_size(pic)

        viewing_boost = request.POST.get('viewing_boost')
        viewing_boost = True if (viewing_boost is not None and viewing_boost.lower() == 'true') else False
        if (not printer.current_print) or viewing_boost:
            # Not need for failure detection if not printing, or the pic was send for viewing boost.
            pic_path = f'snapshots/{printer.id}/latest_unrotated.jpg'
            internal_url, external_url = save_file_obj(pic_path, pic, settings.PICS_CONTAINER, user.syndicate.name, long_term_storage=False)
            cache.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)
            send_status_to_web(printer.id)
            return Response({'result': 'ok'})

        pic_id = str(timezone.now().timestamp())
        pic_path = f'raw/{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
        internal_url, external_url = save_file_obj(pic_path, pic, settings.PICS_CONTAINER, user.syndicate.name, long_term_storage=False)

        img_url_updated = self.detect_if_needed(printer, pic, pic_id, internal_url)
        if not img_url_updated:
            cache.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)

        send_status_to_web(printer.id)
        return Response({'result': 'ok'})

    def detect_if_needed(self, printer, pic, pic_id, raw_pic_url):
        '''
        Return:
           True: Detection was performed. img_url was updated to the tagged image
           False: No detection was performed. img_url was not updated
        '''

        if not printer.should_watch() or not printer.actively_printing():
            return False

        prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)

        if time.time() - prediction.updated_at.timestamp() < settings.MIN_DETECTION_INTERVAL:
            return False

        cache.print_num_predictions_incr(printer.current_print.id)

        req = requests.get(settings.ML_API_HOST + '/p/', params={'img': raw_pic_url}, headers=ml_api_auth_headers(), verify=False)
        req.raise_for_status()
        detections = req.json()['detections']
        if settings.DEBUG:
            LOGGER.info(f'Detections: {detections}')

        update_prediction_with_detections(prediction, detections, printer)
        prediction.save()

        if prediction.current_p > settings.THRESHOLD_LOW * 0.2:  # Select predictions high enough for focused feedback
            cache.print_high_prediction_add(printer.current_print.id, prediction.current_p, pic_id)

        pic.file.seek(0)  # Reset file object pointer so that we can load it again
        tagged_img = io.BytesIO()
        detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
        overlay_detections(Image.open(pic), detections_to_visualize).save(tagged_img, "JPEG")
        tagged_img.seek(0)

        pic_path = f'tagged/{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
        _, external_url = save_file_obj(pic_path, tagged_img, settings.PICS_CONTAINER, printer.user.syndicate.name, long_term_storage=False)
        cache.printer_pic_set(printer.id, {'img_url': external_url}, ex=IMG_URL_TTL_SECONDS)

        prediction_json = serializers.serialize("json", [prediction, ])
        p_out = io.BytesIO()
        p_out.write(prediction_json.encode('UTF-8'))
        p_out.seek(0)
        save_file_obj(f'p/{printer.id}/{printer.current_print.id}/{pic_id}.json', p_out, settings.PICS_CONTAINER, printer.user.syndicate.name, long_term_storage=False)

        if is_failing(prediction, printer.detective_sensitivity, escalating_factor=settings.ESCALATING_FACTOR):
            # The prediction is high enough to match the "escalated" level and hence print needs to be paused
            pause_if_needed(printer, external_url)
        elif is_failing(prediction, printer.detective_sensitivity, escalating_factor=1):
            alert_if_needed(printer, external_url)

        return True

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
                'retract_on_pause': printer.retract_on_pause,
            }
        })

    def get(self, request):
        return self.get_response(request.auth, request.user)

    def patch(self, request):
        Printer.objects.filter(id=request.auth.id).update(**request.data)
        return self.get_response(request.auth, request.user)


# Helper methods

def alert_should_be_suppressed(current_print):
    if not current_print:
        return True

    last_alerted = current_print.alerted_at or datetime.fromtimestamp(0, timezone.utc)
    if (timezone.now() - last_alerted).total_seconds() < ALERT_COOLDOWN_SECONDS:
        return True

    last_acknowledged = current_print.alert_acknowledged_at or datetime.fromtimestamp(0, timezone.utc)
    return last_alerted > last_acknowledged


def alert_if_needed(printer, img_url):
    if not printer.should_watch() or alert_should_be_suppressed(printer.current_print):
        return
    printer.set_alert()
    send_failure_alert(printer, img_url, is_warning=True, print_paused=False)


def pause_if_needed(printer, img_url):
    if not printer.should_watch():
        return

    printer_paused = False
    if printer.action_on_failure == Printer.PAUSE and not printer.current_print.paused_at:
        last_acknowledged = printer.current_print.alert_acknowledged_at or datetime.fromtimestamp(0, timezone.utc)
        if (timezone.now() - last_acknowledged).total_seconds() < ALERT_COOLDOWN_SECONDS: # If user has acknowledged a previous alert, and it's in cooldown period, don't pause otherwise it can be annoying
            return

        # print.paused_at is used to prevent pausing multiple times in case of detected failure. Set it to prevent it.
        printer.current_print.paused_at = timezone.now()
        printer.current_print.save()

        printer.pause_print(initiator='system')
        printer_paused = True
    elif alert_should_be_suppressed(printer.current_print):
        return

    printer.set_alert()
    send_failure_alert(printer, img_url, is_warning=False, print_paused=printer_paused)


def cap_image_size(pic):
    try:
        im = Image.open(pic.file)
    except UnidentifiedImageError:
        raise ValidationError('Corrupted image.')

    im = Image.open(pic.file)
    if max(im.size) <= 1296:
        pic.file.seek(0)
        return pic

    im.thumbnail((1280, 960), Image.LANCZOS)
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

        otp_response = None
        if 'one_time_passcode' in request.data: # For the agent that supports OTP
            one_time_passcode = request.data.pop('one_time_passcode')
            # When the user sends a one-time passcode, it is associated with the verification_code
            (maybe_new_one_time_passcode, verification_code) = request_one_time_passcode(one_time_passcode)
            otp_response = {
                'one_time_passcode': maybe_new_one_time_passcode,
                'one_time_passlink': f'https://obico.onelink.me/fxEU/3ajxjqzd?deep_link_value=https://app.obico.io/printers/wizard/link/?one_time_passcode={maybe_new_one_time_passcode}',
                'verification_code': verification_code}

        messages = []
        device_info = request.data

        device_host_or_ip, _ = IpWare().get_client_ip({'REMOTE_ADDR': device_info['host_or_ip']}) # Tricky IPWare into returning an IP address without request.META

        if device_host_or_ip and device_host_or_ip.is_private:
            device_info['host_or_ip'] = str(device_host_or_ip)

            update_presence_for_device(
                client_ip=client_ip,
                device_id=device_info['device_id'],
                device_info=device_info,
            )

            messages = pull_messages_for_device(
                client_ip=client_ip,
                device_id=device_info['device_id'],
            )

        discovery_response = {'messages': [m.asdict() for m in messages]}
        if otp_response:
            discovery_response.update(otp_response)

        return Response(discovery_response)


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
            return Response({'detail': "Requested resource does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PrinterEventView(CreateAPIView):
    authentication_classes = (PrinterAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PrinterEvent.objects.filter(printer=self.request.auth)

    def post(self, request):
        printer = request.auth

        rotated_jpg_url = None
        if 'snapshot' in request.FILES:
            pic = request.FILES['snapshot']
            pic = cap_image_size(pic)
            # Snapshots for event are short term by nature. Save them to short term storage
            rotated_jpg_url = save_pic(
                        f'snapshots/{printer.id}/{str(timezone.now().timestamp())}_rotated.jpg',
                        pic,
                        request.user.syndicate.name,
                        rotated=True,
                        printer_settings=printer.settings,
                        to_long_term_storage=False,
            )

        print_event = PrinterEvent.create(
            printer=printer,
            print=printer.current_print,
            event_type=request.data.get('event_type'),
            event_class=request.data.get('event_class'),
            event_title=request.data.get('event_title'),
            event_text=request.data.get('event_text').replace('\x00', ''), # For unknown reason some events contains null bytes
            info_url=request.data.get('info_url'),
            image_url=rotated_jpg_url,
            task_handler=request.data.get('notify', '').lower() in ['t', 'true'],
        )
        return Response({'result': 'ok'})

class GCodeFileView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    authentication_classes = (PrinterAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = GCodeFileSerializer

    def get_queryset(self):
        return GCodeFile.objects.filter(user=self.request.user)

    # Post to this endpoint is considered an upsert, identified by resident_printer + agent_signature + safe_filename
    # Agent is required to upsert a GCodeFile before or during a print so that the Print can be linked to a GCodeFile
    def post(self, request):
        printer = request.auth

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Overwrite the foreign keys as they are not supposed to be set by the agent.
        validated_data['resident_printer_id'] = printer.id
        validated_data['user_id'] = request.user.id

        (g_code_file, created) = self.get_queryset().filter(
            Q(resident_printer=printer) | Q(resident_printer__isnull=True), # Matching g-code can either reside in the requesting agent, or in the cloud.
            ).get_or_create(
                agent_signature=validated_data['agent_signature'],
                safe_filename=validated_data['safe_filename'],
                defaults=validated_data,
            )
        return Response(
            self.get_serializer(g_code_file).data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            )

    def partial_update(self, request, pk=None):
        instance = self.get_queryset().filter(pk=pk).first()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
