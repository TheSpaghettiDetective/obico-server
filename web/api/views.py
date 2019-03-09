from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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
        self.current_printer_or_404(pk).cancel_print()
        return self.send_response(pk)

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        self.current_printer_or_404(pk).pause_print()
        return self.send_response(pk)

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        self.current_printer_or_404(pk).resume_print(mute_alert=request.GET.get('mute_alert', None))
        return self.send_response(pk)

    @action(detail=True, methods=['get'])
    def acknowledge_alert(self, request, pk=None):
        self.current_printer_or_404(pk).acknowledge_alert()
        return self.send_response(pk)

    def send_response(self, pk):
        send_commands_to_group(pk)
        return Response({'status': 'OK'})

    def current_printer_or_404(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)
