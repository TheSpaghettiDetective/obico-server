from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import PrinterServiceTokenAuthentication
from app.models import Printer
from api.serializers import PublicPrinterSerializer


class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (PrinterServiceTokenAuthentication,)
    serializer_class = PublicPrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    def list(self, request):
        printer = request.auth

        serializer = self.serializer_class(printer, many=False)
        return Response(serializer.data)
