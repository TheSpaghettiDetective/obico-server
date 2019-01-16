from django.shortcuts import render, redirect
from django.views import View

from .models import *

# Create your views here.
def index(request):
    return redirect('/printers/')

class PrinterView(View):

    def get(self, request):
        printers = Printer.objects.filter(user=request.user)
        return render(request, 'printers_grid.html', {'printers': printers})
