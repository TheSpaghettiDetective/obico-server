from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from app.models import *
from lib import redis
from .serializers import *

from lib.channels import send_commands_to_group

class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cancel_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.cancel_print()
        return self.send_command_response(printer)

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.pause_print()
        return self.send_command_response(printer)

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.resume_print(mute_alert=request.GET.get('mute_alert', None))
        return self.send_command_response(printer)

    @action(detail=True, methods=['get'])
    def mute_current_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.mute_current_print(request.GET.get('mute_alert', 'false').lower() == 'true')
        return self.send_command_response(printer)

    @action(detail=True, methods=['get'])
    def acknowledge_alert(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.acknowledge_alert(request.GET.get('alert_overwrite'))
        return self.send_command_response(printer)

    def send_command_response(self, printer):
        send_commands_to_group(printer.id)
        serializer = PrinterSerializer(printer)
        return Response(serializer.data)

    def current_printer_or_404(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)


class PrintViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Print.objects.filter(printer__user=self.request.user)

    @action(detail=True, methods=['get'])
    def alert_overwrite(self, request, pk=None):
        print = get_object_or_404(self.get_queryset(), pk=pk)
        print.alert_overwrite = request.GET.get('value', None)
        print.save()
        credit = UserCredit.objects.create(user=request.user, print=print, reason=UserCredit.ALERT_OVERWRITE, amount=4)
        serializer = UserCreditSerializer(credit)
        return Response(serializer.data)

