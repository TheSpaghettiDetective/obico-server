from django.shortcuts import render
from django.views import View
from rest_framework.permissions import IsAuthenticated

from .models import *

# Create your views here.
def index(request):
    return render(request, 'index.html')


class PrinterView(View):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        printers = Printer.objects.filter(user=request.user)
        return render(request, 'printer_gallery.html', {'printers': printers})
