from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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
        get_object_or_404(self.get_queryset, id=pk).queue_octoprint_command('cancel')
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        get_object_or_404(self.get_queryset, id=pk).queue_octoprint_command('pause')
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        if request.GET.get('mute_alert', None):
            printer = self.current_printer(pk)
            printer.current_print_alert_muted = True
            printer.save()

        get_object_or_404(self.get_queryset, id=pk).queue_octoprint_command('resume')
        return Response({'status': 'OK'})

    def current_printer(self, pk):
        return self.get_queryset().filter(id=pk).first()
