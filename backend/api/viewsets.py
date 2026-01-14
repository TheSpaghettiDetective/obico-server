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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from random import random, seed
from rest_framework.throttling import AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
import requests
from ipware import get_client_ip
import json
import pytz
from datetime import timedelta, datetime
from django.utils.dateparse import parse_datetime
from django.db.models.functions import TruncDay
from django.db.models import Sum, Max, Count, fields, Case, Value, When

from .utils import report_validationerror
from .authentication import CsrfExemptSessionAuthentication
from app.models import (
    User, Print, Printer, GCodeFile, PrintShotFeedback, PrinterPrediction, MobileDevice, OneTimeVerificationCode,
    SharedResource, OctoPrintTunnel, calc_normalized_p, NotificationSetting, PrinterEvent, GCodeFolder, FirstLayerInspectionImage)
from .serializers import (
    UserSerializer, GCodeFileSerializer, GCodeFileDeSerializer, PrinterSerializer, PrintSerializer, MobileDeviceSerializer,
    PrintShotFeedbackSerializer, OneTimeVerificationCodeSerializer, SharedResourceSerializer, OctoPrintTunnelSerializer,
    NotificationSettingSerializer, PrinterEventSerializer, GCodeFolderDeSerializer, GCodeFolderSerializer, FirstLayerInspectionImageSerializer
)
from lib.channels import send_status_to_web
from lib import cache, gcode_metadata
from lib.view_helpers import get_printer_or_404
from config.celery import celery_app
from lib.file_storage import save_file_obj, delete_file
from lib.printer_discovery import (
    push_message_for_device,
    get_active_devices_for_client_ip,
    DeviceMessage,
)
from lib.one_time_passcode import check_one_time_passcode
from notifications.handlers import handler

LOGGER = logging.getLogger(__file__)

PREDICTION_FETCH_TIMEOUT = 20


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = PrinterSerializer

    def get_queryset(self):
        if self.request.query_params.get('with_archived') == 'true':
            qs = Printer.with_archived.filter(user=self.request.user)
        else:
            qs = Printer.objects.filter(user=self.request.user)

        return qs.select_related('current_print', 'printerprediction', 'user')

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        printer = get_printer_or_404(pk, request)
        printer.archived_at = timezone.now()
        printer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        if not printer.current_print:
            raise Http404('Not currently printing')

        printer.current_print.alert_acknowledged(request.GET.get('alert_overwrite'))
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = PrintSerializer

    def get_queryset(self):
        with_deleted = self.request.GET.get('with_deleted', None) is not None
        queryset = Print.objects.all_with_deleted() if with_deleted else Print.objects
        queryset = queryset.filter(
            user=self.request.user,
            )

        filter = self.request.GET.get('filter', 'none')
        if filter == 'cancelled':
            queryset = queryset.filter(cancelled_at__isnull=False)
        if filter == 'finished':
            queryset = queryset.filter(finished_at__isnull=False)
        # FIXME: remove when mobile app will use separate filters (below) for feedback_needed:
        if filter == 'need_alert_overwrite':
            queryset = queryset.filter(alert_overwrite__isnull=True, tagged_video_url__isnull=False)
        if filter == 'need_print_shot_feedback':
            queryset = queryset.filter(printshotfeedback__isnull=False, printshotfeedback__answered_at__isnull=True).distinct()

        feedback_filter = self.request.GET.get('feedback_needed', 'none')
        if feedback_filter == 'need_alert_overwrite':
            queryset = queryset.filter(alert_overwrite__isnull=True, tagged_video_url__isnull=False)
        if feedback_filter == 'need_print_shot_feedback':
            queryset = queryset.filter(printshotfeedback__isnull=False, printshotfeedback__answered_at__isnull=True).distinct()

        if 'from_date' in self.request.GET:
            tz = pytz.timezone(self.request.GET['timezone'])
            from_date = timezone.make_aware(parse_datetime(f'{self.request.GET["from_date"]}T00:00:00'), timezone=tz)
            to_date = timezone.make_aware(parse_datetime(f'{self.request.GET["to_date"]}T23:59:59'), timezone=tz)
            queryset = queryset.filter(started_at__range=[from_date, to_date])

        filter_by_printer_ids = self.request.GET.getlist('filter_by_printer_ids[]')
        if filter_by_printer_ids:
            queryset = queryset.filter(printer_id__in=filter_by_printer_ids)

        return queryset

    def list(self, request):
        queryset = self.get_queryset().prefetch_related('printshotfeedback_set'
            ).select_related('printer', 'g_code_file', 'printer__user'
            )

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
            pred = PrinterPrediction(**raw_pred['fields'])
            raw_pred['fields']['normalized_p'] = calc_normalized_p(
                detective_sensitivity, pred)

        return Response(
            data,
            headers={k: v for k, v in resp_headers.items() if v is not None}
        )

    @action(detail=False, methods=['get', ])
    def stats(self, request):

        def datetime_periods_by_week(from_date, to_date, period):
            datetime_periods = [from_date,next_period_start_after(from_date, period)]
            while datetime_periods[-1] <= to_date:
                datetime_periods.append(next_period_start_after(datetime_periods[-1], period))
            return datetime_periods

        def next_period_start_after(date_time, period):
            if period == 'day':
                next_period_start = date_time + timedelta(days=1)
            elif period == 'week':
                day_of_week = date_time.weekday()
                days_until_sunday = 6 - day_of_week
                if days_until_sunday == 0:
                    days_until_sunday = 7
                next_period_start = date_time + timedelta(days=days_until_sunday)
            elif period == 'month':
                next_month = date_time.month + 1 if date_time.month < 12 else 1
                next_year = date_time.year + 1 if next_month == 1 else date_time.year
                next_period_start = datetime(next_year, next_month, 1, tzinfo=date_time.tzinfo)
            elif period == 'year':
                next_year = date_time.year + 1
                next_period_start = datetime(next_year, 1, 1, tzinfo=date_time.tzinfo)

            return next_period_start.replace(hour=0, minute=0, second=0, microsecond=0)


        tz = pytz.timezone(request.GET['timezone'].replace(' ', '+'))
        from_date = timezone.make_aware(parse_datetime(f'{request.GET["from_date"]}T00:00:00'), timezone=tz)
        to_date = timezone.make_aware(parse_datetime(f'{request.GET["to_date"]}T23:59:59'), timezone=tz)
        group_by = request.GET['group_by'].lower()

        queryset = queryset = self.get_queryset().annotate(
                date=TruncDay('started_at', tzinfo=tz),
            ).values('date').annotate(
                filament_used=Sum('filament_used'),
                total_print_time=Sum('print_time'),
                longest_print_time=Max('print_time'),
                print_count=Count('*'),
                cancelled_print_count=Sum(Case(When(cancelled_at=None, then=Value(0)), default=Value(1), output_field=fields.IntegerField())),
            ).order_by('date')

        all_days = queryset.all()

        print_count_groups = []
        print_time_groups = []
        filament_used_groups = []
        cancelled_print_count_groups = []

        group_periods = datetime_periods_by_week(from_date, to_date, group_by)
        for i in range(len(group_periods) - 1):
            period_start = group_periods[i]
            period_end = group_periods[i+1]

            group_key = period_start.isoformat()

            all_days_in_current_period = [day for day in all_days if period_start <= day['date'] < period_end]

            print_count_groups.append( dict( key=group_key, value=sum([d['print_count'] for d in all_days_in_current_period]) ) )
            print_time_groups.append( dict( key=group_key, value=sum([d['total_print_time'] for d in all_days_in_current_period if d['total_print_time'] is not None]) ) )
            filament_used_groups.append( dict( key=group_key, value=sum([d['filament_used'] for d in all_days_in_current_period if d['filament_used'] is not None]) ) )
            cancelled_print_count_groups.append( dict( key=group_key, value=sum([d['cancelled_print_count'] for d in all_days_in_current_period]) ) )

        result = {
            'print_count_groups': print_count_groups,
            'print_time_groups': print_time_groups,
            'filament_used_groups': filament_used_groups,
            'total_print_count': sum([g['value'] for g in print_count_groups]),
            'total_print_time': sum([g['value'] for g in print_time_groups]),
            'total_filament_used': sum([g['value'] for g in filament_used_groups]),
            'total_cancelled_print_count':  sum([g['value'] for g in cancelled_print_count_groups]),
            'longest_print_time': max([d['longest_print_time'] or 0 for d in all_days]) if all_days else 0,
        }
        result['average_print_time'] = result['total_print_time'] / result['total_print_count'] if result['total_print_count'] > 0 else 0
        result['total_succeeded_print_count'] = result['total_print_count'] - result['total_cancelled_print_count']

        return Response(result)

class GCodeFolderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GCodeFolderSerializer
        else:
            return GCodeFolderDeSerializer

    def get_queryset(self):
        return GCodeFolder.objects.filter(user=self.request.user,)

    def list(self, request):
        qs = self.get_queryset().select_related(
            'parent_folder')

        sorting = request.GET.get('sorting', 'created_at_desc')
        if sorting == 'created_at_asc':
            qs = qs.order_by('id')
        elif sorting == 'created_at_desc':
            qs = qs.order_by('-id')
        elif sorting == 'name_asc':
            qs = qs.order_by('name')
        elif sorting == 'name_desc':
            qs = qs.order_by('-name')

        if 'parent_folder' in request.GET:
            parent_folder = request.GET.get('parent_folder')
            if parent_folder == 'null' or parent_folder == '':
                qs = qs.filter(parent_folder__isnull=True)
            else:
                qs = qs.filter(parent_folder_id=int(parent_folder))

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        folder_ids = request.data.get('folder_ids', [])
        self.get_queryset().filter(id__in=folder_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def bulk_move(self, request):
        folder_ids = request.data.get('folder_ids', [])
        self.get_queryset().filter(id__in=folder_ids).update(
            parent_folder_id=request.data.get('parent_folder') or None)
        return Response(status=status.HTTP_204_NO_CONTENT)

class GCodeFileViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GCodeFileSerializer
        else:
            return GCodeFileDeSerializer

    def get_queryset(self):
        qs = GCodeFile.objects
        if 'pk' in self.kwargs:
            qs = qs.all_with_deleted()
        return qs.filter(user=self.request.user)

    def list(self, request):
        qs = self.get_queryset().select_related(
            'parent_folder').prefetch_related(
            'print_set__printer')

        sorting = request.GET.get('sorting', 'created_at_desc')
        if sorting == 'created_at_asc':
            qs = qs.order_by('id')
        elif sorting == 'created_at_desc':
            qs = qs.order_by('-id')
        elif sorting == 'num_bytes_asc':
            qs = qs.order_by('num_bytes')
        elif sorting == 'num_bytes_desc':
            qs = qs.order_by('-num_bytes')
        elif sorting == 'filename_asc':
            qs = qs.order_by('filename')
        elif sorting == 'filename_desc':
            qs = qs.order_by('-filename')

        q = request.GET.get('q')
        if q:
            qs = qs.filter(safe_filename__icontains=q)

        if 'parent_folder' in request.GET:
            parent_folder = request.GET.get('parent_folder')
            if parent_folder == 'null' or parent_folder == '':
                qs = qs.filter(parent_folder__isnull=True)
            else:
                qs = qs.filter(parent_folder_id=int(parent_folder))

        if 'safe_filename' in request.GET and 'agent_signature' in request.GET:
            qs = qs.filter(agent_signature=request.GET.get('agent_signature'),
                           safe_filename=request.GET.get('safe_filename'))

        resident_printer = request.GET.get('resident_printer')
        if resident_printer:
            qs = qs.filter(resident_printer=resident_printer)
        else:
            qs = qs.filter(resident_printer__isnull=True)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        file_ids = request.data.get('file_ids', [])
        self.get_queryset().filter(id__in=file_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def bulk_move(self, request):
        file_ids = request.data.get('file_ids', [])
        self.get_queryset().filter(id__in=file_ids).update(
            parent_folder_id=request.data.get('parent_folder') or None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        gcode_file = GCodeFile.objects.create(**validated_data)

        if 'file' in request.FILES:
            file_size_limit = 500 * 1024 * 1024 if request.user.is_pro else 50 * 1024 * 1024
            num_bytes=request.FILES['file'].size
            if num_bytes > file_size_limit:
                return Response({'error': 'File size too large'}, status=413)

            self.set_metadata(gcode_file, *gcode_metadata.parse(request.FILES['file'], num_bytes, request.encoding or settings.DEFAULT_CHARSET), request.user.syndicate.name)

            request.FILES['file'].seek(0)
            _, ext_url = save_file_obj(self.path_in_storage(gcode_file), request.FILES['file'], settings.GCODE_CONTAINER, request.user.syndicate.name)
            gcode_file.url = ext_url
            gcode_file.num_bytes = num_bytes
            gcode_file.save()

        return Response(self.get_serializer(instance=gcode_file, many=False).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        gcode_file = self.get_object()

        # Delete the file from storage, and set url to None before soft-deleting a g-code file
        delete_file(self.path_in_storage(gcode_file), settings.GCODE_CONTAINER)
        gcode_file.url = None
        gcode_file.save()

        gcode_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def set_metadata(self, gcode_file, metadata, thumbnails, syndicate_name):
        gcode_file.metadata_json = json.dumps(metadata)
        for key in ['estimated_time', 'filament_total']:
            setattr(gcode_file, key, metadata.get(key))

        thumb_num = 0
        for thumb in sorted(thumbnails, key=lambda x: x.getbuffer().nbytes, reverse=True):
            thumb_num += 1
            if thumb_num > 3:
                continue
            _, ext_url = save_file_obj(f'gcode_thumbnails/{gcode_file.user.id}/{gcode_file.id}/{thumb_num}.png', thumb, settings.TIMELAPSE_CONTAINER, syndicate_name)
            setattr(gcode_file, f'thumbnail{thumb_num}_url', ext_url)

    def path_in_storage(self, gcode_file):
        return f'{gcode_file.user.id}/{gcode_file.id}'


class PrintShotFeedbackViewSet(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = PrintShotFeedbackSerializer

    def get_queryset(self):
        try:
            print_id = int(self.request.query_params.get('print_id'))
        except (ValueError, TypeError):
            print_id = None

        qs = PrintShotFeedback.objects.filter(
            print__user=self.request.user
        ).select_related('print__user')

        if print_id:
            qs = qs.filter(print_id=print_id)

        return qs

    def update(self, request, *args, **kwargs):
        unanswered_print_shots = self.get_queryset().filter(answered_at__isnull=True)
        should_credit = len(unanswered_print_shots) == 1 and unanswered_print_shots.first().id == int(kwargs['pk'])

        if should_credit:
            _print = unanswered_print_shots.first().print
            celery_app.send_task('app_ent.tasks.base_tasks.credit_dh_for_contribution',
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)

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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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


class OneTimePasscodeViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        verification_code = request.data.get('verification_code')
        one_time_passcode = request.data.get('one_time_passcode')

        verification_code_obj = get_object_or_404(OneTimeVerificationCode, user=request.user, code=verification_code)

        if not check_one_time_passcode(one_time_passcode, verification_code_obj.code):
            return JsonResponse({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({'detail': 'OK'}, status=status.HTTP_200_OK)


class PrinterDiscoveryViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        MAX_UNLINKED_PRINTERS_PER_IP = 2

        client_ip, is_routable = get_client_ip(request)

        # must guard against possible None or blank value as client_ip
        if not client_ip:
            raise ImproperlyConfigured("cannot determine client_ip")

        devices = get_active_devices_for_client_ip(client_ip)
        if len(devices) > MAX_UNLINKED_PRINTERS_PER_IP:
            return Response([])
        return Response([device for device in devices])

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
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
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


class PrinterEventViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = PrinterEventSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return PrinterEvent.objects.filter(printer__user=self.request.user).order_by('-id')

    def list(self, request):
        queryset = self.get_queryset()

        filter_by_classes = request.GET.getlist('filter_by_classes[]', [])
        queryset = queryset.filter(event_class__in=filter_by_classes)

        filter_by_types = []
        for type_filter in request.GET.getlist('filter_by_types[]', []):
            if type_filter == 'ALERT':
                filter_by_types += [PrinterEvent.FAILURE_ALERTED, PrinterEvent.ALERT_MUTED, PrinterEvent.ALERT_UNMUTED,]
            elif type_filter == 'PAUSE_RESUME':
                filter_by_types += [PrinterEvent.PAUSED, PrinterEvent.RESUMED,]
            else:
                filter_by_types += [type_filter,]
        queryset = queryset.filter(event_type__in=filter_by_types)

        start = int(request.GET.get('start', '0'))
        limit = int(request.GET.get('limit', '12'))
        # The "right" way to do it is `queryset[start:start+limit]`. However, it slows down the query by 100x because of the "offset 12 limit 12" clause. Weird.
        # Maybe related to https://stackoverflow.com/questions/21385555/postgresql-query-very-slow-with-limit-1
        results = list(queryset)[start:start + limit]

        serializer = self.serializer_class(results, many=True)
        return Response(serializer.data)


class FirstLayerInspectionImageViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)
    serializer_class = FirstLayerInspectionImageSerializer

    def get_queryset(self):
        queryset = FirstLayerInspectionImage.objects.filter(first_layer_inspection__print__user=self.request.user)
        print_id = self.request.GET.get('print_id', None)

        if print_id:
            queryset = queryset.filter(first_layer_inspection__print_id=print_id)

        return queryset


class ApiVersionView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, OAuth2Authentication)

    def get(self, request, format=None):
        return Response({'version': '1.0.0'})