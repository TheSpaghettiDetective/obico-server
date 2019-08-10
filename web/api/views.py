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
        succeeded, alert_acknowledged = printer.cancel_print()
        return self.send_command_response(printer, succeeded, alert_acknowledged)

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded, alert_acknowledged = printer.pause_print()
        return self.send_command_response(printer, succeeded, alert_acknowledged)

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        succeeded, alert_acknowledged = printer.resume_print(mute_alert=request.GET.get('mute_alert', None))
        return self.send_command_response(printer, succeeded, alert_acknowledged)

    @action(detail=True, methods=['get'])
    def mute_current_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        printer.mute_current_print(request.GET.get('mute_alert', 'false').lower() == 'true')
        return self.send_command_response(printer, True, False)

    @action(detail=True, methods=['get'])
    def acknowledge_alert(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        alert_acknowledged = printer.acknowledge_alert(request.GET.get('alert_overwrite'))
        return self.send_command_response(printer, alert_acknowledged, alert_acknowledged)

    def send_command_response(self, printer, succeeded, alert_acknowledged):
        send_commands_to_group(printer.id)
        return Response(dict(succeeded=succeeded, alert_acknowledged=alert_acknowledged))

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


class UserCreditViewSet(viewsets.ModelViewSet):
    serializer_class = UserCreditSerializer

    def get_queryset(self):
        return UserCredit.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def total(self, request, pk=None):
        user_credits = self.get_queryset()
        total_credits = sum([c.amount for c in user_credits])
        return Response({'count': total_credits})
