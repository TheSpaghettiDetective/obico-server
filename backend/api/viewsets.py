from django.shortcuts import get_object_or_404
from django.http import Http404
import os
import time
import logging
from binascii import hexlify
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from random import random, seed
from rest_framework.throttling import AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
import requests
from ipware import get_client_ip

from .utils import report_validationerror
from .authentication import CsrfExemptSessionAuthentication
from app.models import (
    User, Print, Printer, GCodeFile, PrintShotFeedback, PrinterPrediction, MobileDevice, OneTimeVerificationCode,
    SharedResource, OctoPrintTunnel, calc_normalized_p, NotificationSetting)
from .serializers import (
    UserSerializer, GCodeFileSerializer, PrinterSerializer, PrintSerializer, MobileDeviceSerializer,
    PrintShotFeedbackSerializer, OneTimeVerificationCodeSerializer, SharedResourceSerializer, OctoPrintTunnelSerializer,
    NotificationSettingSerializer,
)
from lib.channels import send_status_to_web
from lib import cache
from lib.view_helpers import get_printer_or_404
from config.celery import celery_app
from .printer_discovery import (
    push_message_for_device,
    get_active_devices_for_client_ip,
    DeviceMessage,
)
from notifications.handlers import handler

LOGGER = logging.getLogger(__file__)

PREDICTION_FETCH_TIMEOUT = 20


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = UserSerializer

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = self.serializer_class(user, data=request.data, partial=True)  # set partial=True to update a data partially
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user.refresh_from_db()
        else:
            serializer = self.serializer_class(user, many=False)

        return Response(serializer.data)


class PrinterViewSet(
    # FIXME arbitrary update IS allowed, right?
    # no create, no destroy
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = PrinterSerializer

    def get_queryset(self):
        if self.request.query_params.get('with_archived') == 'true':
            return Printer.with_archived.filter(user=self.request.user)
        else:
            return Printer.objects.filter(user=self.request.user)

    # TODO: Remove the "GET" method after old mobile app versions have faded

    @action(detail=True, methods=['post', 'get'])
    def cancel_print(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        succeeded = printer.cancel_print(initiator='api')

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['post', 'get'])
    def pause_print(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        succeeded = printer.pause_print(initiator='api')

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['post', 'get'])
    def resume_print(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        succeeded = printer.resume_print(initiator='api')

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['post', 'get'])
    def mute_current_print(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        printer.mute_current_print(request.GET.get('mute_alert', 'false').lower() == 'true')

        return self.send_command_response(printer, True)

    @action(detail=True, methods=['post', 'get'])
    def acknowledge_alert(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        printer.acknowledge_alert(request.GET.get('alert_overwrite'))

        return self.send_command_response(printer, True)

    @action(detail=True, methods=['post'])
    def send_command(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        printer.send_octoprint_command(request.data['cmd'], request.data['args'])

        return self.send_command_response(printer, True)

    def partial_update(self, request, pk=None):
        self.get_queryset().filter(pk=pk).update(**request.data)
        printer = get_printer_or_404(pk, request)
        printer.send_should_watch_status()

        return self.send_command_response(printer, True)

    def send_command_response(self, printer, succeeded):
        send_status_to_web(printer.id)
        serializer = self.serializer_class(printer)

        return Response(dict(succeeded=succeeded, printer=serializer.data))


class PrintViewSet(
    # no create
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = PrintSerializer

    def get_queryset(self):
        return Print.objects.filter(user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset().prefetch_related('printshotfeedback_set').filter(video_url__isnull=False)
        filter = request.GET.get('filter', 'none')
        if filter == 'cancelled':
            queryset = queryset.filter(cancelled_at__isnull=False)
        if filter == 'finished':
            queryset = queryset.filter(finished_at__isnull=False)
        if filter == 'need_alert_overwrite':
            queryset = queryset.filter(alert_overwrite__isnull=True, tagged_video_url__isnull=False)
        if filter == 'need_print_shot_feedback':
            queryset = queryset.filter(printshotfeedback__isnull=False, printshotfeedback__answered_at__isnull=True).distinct()

        sorting = request.GET.get('sorting', 'date_desc')
        if sorting == 'date_asc':
            queryset = queryset.order_by('id')
        else:
            queryset = queryset.order_by('-id')

        start = int(request.GET.get('start', '0'))
        limit = int(request.GET.get('limit', '12'))
        # The "right" way to do it is `queryset[start:start+limit]`. However, it slows down the query by 100x because of the "offset 12 limit 12" clause. Weird.
        # Maybe related to https://stackoverflow.com/questions/21385555/postgresql-query-very-slow-with-limit-1
        results = list(queryset)[start:start + limit]

        serializer = self.serializer_class(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        select_prints_ids = request.data.get('print_ids', [])
        self.get_queryset().filter(id__in=select_prints_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def prediction_json(self, request, pk) -> Response:
        p: Print = get_object_or_404(
            self.get_queryset().select_related('printer'),
            pk=pk)

        # check as it's null=True
        if not p.prediction_json_url:
            return Response([])

        headers = {
            'If-Modified-Since': request.headers.get('if-modified-since'),
            'If-None-Match': request.headers.get('if-none-match'),
        }

        r = requests.get(url=p.prediction_json_url,
                         timeout=PREDICTION_FETCH_TIMEOUT,
                         headers={k: v for k, v in headers.items() if v is not None})
        r.raise_for_status()

        resp_headers = {
            'Last-Modified': r.headers.get('Last-Modified'),
            'Etag': r.headers.get('Etag')
        }

        # might be cached already
        if r.status_code == 304:
            return Response(
                None,
                status=304,
                headers={k: v for k, v in resp_headers.items() if v is not None}
            )

        data = r.json()

        detective_sensitivity: float = (
            p.printer.detective_sensitivity
            if p.printer is not None else
            Printer._meta.get_field('detective_sensitivity').get_default()
        )

        for raw_pred in data:
            if 'fields' not in raw_pred:
                # once upon a time in production
                # should not happen, exact cause is TODO/FIXME
                raw_pred['fields'] = {'normalized_p': 0.0}
            else:
                pred = PrinterPrediction(**raw_pred['fields'])
                raw_pred['fields']['normalized_p'] = calc_normalized_p(
                    detective_sensitivity, pred)

        return Response(
            data,
            headers={k: v for k, v in resp_headers.items() if v is not None}
        )


class GCodeFileViewSet(
    # no create, no update
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = GCodeFileSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return GCodeFile.objects.filter(user=self.request.user).order_by('-created_at')

    # TODO: remove this override and go back to DRF's standard pagination impl when we no longer need to support the legacy format.
    def list(self, request, *args, **kwargs):
        page_num = request.GET.get('page')
        if page_num:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            results = self.get_queryset()
            return Response(self.serializer_class(results, many=True).data)


class PrintShotFeedbackViewSet(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = PrintShotFeedbackSerializer

    def get_queryset(self):
        try:
            print_id = int(self.request.query_params.get('print_id'))
        except (ValueError, TypeError):
            print_id = None

        qs = PrintShotFeedback.objects.filter(
            print__user=self.request.user
        )

        if print_id:
            qs = qs.filter(print_id=print_id)

        return qs

    def update(self, request, *args, **kwargs):
        unanswered_print_shots = self.get_queryset().filter(answered_at__isnull=True)
        should_credit = len(unanswered_print_shots) == 1 and unanswered_print_shots.first().id == int(kwargs['pk'])

        if should_credit:
            _print = unanswered_print_shots.first().print
            celery_app.send_task('app_ent.tasks.credit_dh_for_contribution',
                                 args=[request.user.id, 2, f'Credit | Focused Feedback - "{_print.filename[:100]}"', f'ff:p:{_print.id}']
                                 )

        resp = super(PrintShotFeedbackViewSet, self).update(request, *args, **kwargs)
        return Response({'instance': resp.data, 'credited_dhs': 2 if should_credit else 0})


class OctoPrintTunnelViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = OctoPrintTunnelSerializer

    def get_queryset(self):
        return OctoPrintTunnel.objects.filter(printer__user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        printer = get_printer_or_404(validated_data['target_printer_id'], request)
        app_name = validated_data['app_name']

        if not app_name or app_name == OctoPrintTunnel.INTERNAL_APP:
            raise PermissionDenied

        tunnel = OctoPrintTunnel.create(printer, app_name)
        tunnel_endpoint = tunnel.get_basicauth_url(request, tunnel.plain_basicauth_password)
        return Response({'tunnel_endpoint': tunnel_endpoint}, status=status.HTTP_201_CREATED)


class OctoPrintTunnelUsageViewSet(mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        return Response({
            'total': cache.octoprinttunnel_get_stats(self.request.user.id),
            'monthly_cap': self.request.user.tunnel_cap(),
            })


class MobileDeviceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = MobileDeviceSerializer

    def get_queryset(self):
        return MobileDevice.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device, _ = MobileDevice.with_inactive.get_or_create(
            user=request.user,
            device_token=serializer.validated_data['device_token'],
            defaults=serializer.validated_data,
        )

        if device.deactivated_at or device.app_version != request.data['app_version']:
            device.deactivated_at = None
            for attr, value in serializer.validated_data.items():
                setattr(device, attr, value)
            device.save()

        return Response(
            self.serializer_class(device, many=False).data,
            status=status.HTTP_201_CREATED)


class OneTimeVerificationCodeViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = OneTimeVerificationCodeSerializer

    def list(self, request, *args, **kwargs):
        printer_id_to_link = request.GET.get('printer_id')
        if printer_id_to_link:
            code = OneTimeVerificationCode.objects.select_related('printer').filter(
                printer_id=printer_id_to_link,
                user=request.user
            ).first()
        else:
            code = OneTimeVerificationCode.objects.select_related('printer').filter(
                printer__isnull=True,
                user=request.user
            ).first()

        if not code:
            seed()
            while True:
                new_code = '%06d' % (int(random() * 1500450271) % 1000000)
                if not OneTimeVerificationCode.objects.filter(code=new_code):    # doesn't collide with existing code
                    break

            code = OneTimeVerificationCode.objects.create(user=request.user, code=new_code, printer_id=printer_id_to_link)

        return Response(self.serializer_class(code, many=False).data)

    def retrieve(self, request, *args, **kwargs):
        code = get_object_or_404(
            OneTimeVerificationCode.with_expired.select_related('printer').filter(user=request.user),
            pk=kwargs["pk"])
        return Response(self.serializer_class(code, many=False).data)


class SharedResourceViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = SharedResourceSerializer

    def list(self, request):
        return self.response_from_printer(request)

    def create(self, request):
        printer = get_printer_or_404(request.GET.get('printer_id'), request)
        # When the GET API is slow, the user may try to turn on the sharing toggle when it's on already
        SharedResource.objects.get_or_create(printer=printer, defaults={'share_token': hexlify(os.urandom(18)).decode()})
        return self.response_from_printer(request)

    def destroy(self, request, pk):
        get_object_or_404(SharedResource.objects.filter(printer__user=request.user), pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def response_from_printer(self, request):
        printer = get_printer_or_404(request.GET.get('printer_id'), request)
        return Response(self.serializer_class(
            SharedResource.objects.select_related('printer').filter(printer=printer),
            many=True)
            .data)


class PrinterDiscoveryViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        MAX_UNLINKED_PRINTERS_PER_IP = 1

        client_ip, is_routable = get_client_ip(request)

        # must guard against possible None or blank value as client_ip
        if not client_ip:
            raise ImproperlyConfigured("cannot determine client_ip")

        devices = get_active_devices_for_client_ip(client_ip)
        if len(devices) > MAX_UNLINKED_PRINTERS_PER_IP:
            return Response([])
        return Response([device.asdict() for device in devices])

    @report_validationerror
    def create(self, request):
        client_ip, is_routable = get_client_ip(request)

        # must guard against possible None or blank value as client_ip
        if not client_ip:
            raise ImproperlyConfigured("cannot determine client_ip")

        code = self.request.data.get('code')
        if code is None:
            raise ValidationError({'code': "missing param"})

        device_id = self.request.data.get('device_id')
        if device_id is None:
            raise ValidationError({'device_id': "missing param"})

        device_secret = self.request.data.get('device_secret')
        if device_secret is None:
            raise ValidationError({'device_secret': "missing param"})

        push_message_for_device(
            client_ip,
            device_id,
            DeviceMessage.from_dict({
                'device_id': device_id,
                'type': 'verify_code',
                'data': {'code': code, 'secret': device_secret}})
        )

        return Response({'queued': True})


class NotificationSettingsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = NotificationSettingSerializer

    def get_queryset(self):
        assert self.request.user.is_anonymous is False
        loaded = (plugin.name for plugin in handler.notification_plugins())
        return NotificationSetting.objects.filter(user=self.request.user, name__in=loaded)

    @action(detail=False, methods=['get', ])
    def available_plugins(self, request):
        loaded = {}
        for plugin in handler.notification_plugins():
            try:
                loaded[plugin.name] = {
                    'features': [
                        feature.name
                        for feature in plugin.instance.supported_features()
                    ],
                    'env_vars': plugin.instance.env_vars(),
                }
            except Exception:
                LOGGER.exception("could not get plugin details")

        return Response({"plugins": loaded})

    @action(detail=True, methods=['post', ])
    def send_test_message(self, request, pk):
        obj = self.get_object()
        try:
            handler.send_test_message(obj)
        except Exception as e:
            LOGGER.exception("cannot test message")
            return Response({"status": "error", "detail": str(e)}, status=418)
        return Response({"status": "sent"})
