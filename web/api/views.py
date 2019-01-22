from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
import json

from app.models import *
from lib import redis
from .serializers import *


class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cancel_print(self, request, pk=None):
        return self.queue_octoprint_command(pk, 'cancel')

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        return self.queue_octoprint_command(pk, 'pause')

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        return self.queue_octoprint_command(pk, 'resume')

    def queue_octoprint_command(self, pk, command):
        printer = self.get_queryset().filter(id=pk).first()
        PrinterCommand.objects.create(printer=printer, command=json.dumps({'cmd': command}), status=PrinterCommand.PENDING)
        redis.printer_status_delete(printer.id, 'alert_outstanding')
        return Response({'status': 'OK'})
