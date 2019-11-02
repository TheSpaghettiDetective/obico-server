from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from app.models import *
from lib import redis
from .serializers import *
from config.celery import celery_app
from lib.channels import send_commands_to_printer

class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cancel_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded, user_credited = printer.cancel_print()
        return self.send_command_response(printer, succeeded, user_credited)

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded, user_credited = printer.pause_print()
        return self.send_command_response(printer, succeeded, user_credited)

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded, user_credited = printer.resume_print(mute_alert=request.GET.get('mute_alert', None))
        return self.send_command_response(printer, succeeded, user_credited)

    @action(detail=True, methods=['get'])
    def mute_current_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.mute_current_print(request.GET.get('mute_alert', 'false').lower() == 'true')
        return self.send_command_response(printer, True, False)

    @action(detail=True, methods=['get'])
    def acknowledge_alert(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        user_credited = printer.acknowledge_alert(request.GET.get('alert_overwrite'))
        return self.send_command_response(printer, user_credited, user_credited)

    def send_command_response(self, printer, succeeded, user_credited):
        send_commands_to_printer(printer.id)
        return Response(dict(succeeded=succeeded, user_credited=user_credited))

    def current_printer_or_404(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)


class PrintViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Print.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def alert_overwrite(self, request, pk=None):
        print = get_object_or_404(self.get_queryset(), pk=pk)

        user_credited = False
        if print.alert_overwrite == None:
            celery_app.send_task('app_ent.tasks.credit_dh_for_contribution', args=[print.printer.user.id, 1, 'Credit: Flag "{}"'.format(print.filename[:100])])
            user_credited = True

        print.alert_overwrite = request.GET.get('value', None)
        print.save()

        return Response(dict(user_credited=user_credited))
