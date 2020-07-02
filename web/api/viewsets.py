from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import requests

from .authentication import CsrfExemptSessionAuthentication
from app.models import *
from .serializers import *
from app.models import PrintShotFeedback
from lib import redis
from lib.channels import send_status_to_web
from config.celery import celery_app


class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = PrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cancel_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded = printer.cancel_print()

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded = printer.pause_print()

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded = printer.resume_print()

        return self.send_command_response(printer, succeeded)

    @action(detail=True, methods=['get'])
    def mute_current_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.mute_current_print(request.GET.get('mute_alert', 'false').lower() == 'true')

        return self.send_command_response(printer, True)

    @action(detail=True, methods=['get'])
    def acknowledge_alert(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.acknowledge_alert(request.GET.get('alert_overwrite'))

        return self.send_command_response(printer, True)

    @action(detail=True, methods=['post'])
    def send_command(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.send_octoprint_command(request.data['cmd'], request.data['args'])

        return self.send_command_response(printer, True)

    @action(detail=True, methods=['get'])
    def send_webhook_test(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        req = requests.post(
            url= settings.EXT_3D_GEEKS_ENDPOINT,
            json=dict(
                token=printer.service_token,
                event="test"))
        req.raise_for_status()

        return Response(dict(status='okay'))

    def partial_update(self, request, pk=None):
        self.get_queryset().filter(pk=pk).update(**request.data)
        printer = self.current_printer_or_404(pk)
        printer.send_should_watch_status()

        return self.send_command_response(printer, True)

    def send_command_response(self, printer, succeeded):
        send_status_to_web(printer.id)
        serializer = self.serializer_class(printer)

        return Response(dict(succeeded=succeeded, printer=serializer.data))

    def current_printer_or_404(self, pk):
        return get_object_or_404(Printer.with_archived.filter(user=self.request.user), pk=pk)


class PrintViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = PrintSerializer

    def get_queryset(self):
        return Print.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def alert_overwrite(self, request, pk=None):
        print = get_object_or_404(self.get_queryset(), pk=pk)

        # TODO: remove this after switching to focused feedback
        if request.method == "GET":
            print.alert_overwrite = request.GET.get('value', None)
            print.save()

            return Response(dict(user_credited=False))
        else:
            print.alert_overwrite = request.data.get('value', None)
            print.save()
            serializer = self.serializer_class(print, many=False)
            return Response(serializer.data)

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
        results = list(queryset)[start:start+limit]

        serializer = self.serializer_class(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        select_prints_ids = request.data.get('print_ids', [])
        self.get_queryset().filter(id__in=select_prints_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GCodeFileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = GCodeFileSerializer

    def get_queryset(self):
        return GCodeFile.objects.filter(user=self.request.user).order_by('-created_at')


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
