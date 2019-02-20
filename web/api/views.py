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
        self.current_printer_or_404(pk).cancel_print()
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        self.current_printer_or_404(pk).pause_print()
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        self.current_printer_or_404(pk).resume_print(mute_alert=request.GET.get('mute_alert', None))
        return Response({'status': 'OK'})

    def current_printer_or_404(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)
