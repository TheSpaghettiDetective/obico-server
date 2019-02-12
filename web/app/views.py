import os
from binascii import hexlify
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from .models import *
from .forms import *

# Create your views here.
def index(request):
    return redirect('/printers/')

@login_required
def printers(request):
    printers = Printer.objects.filter(user=request.user)
    return render(request, 'printer_list.html', {'printers': printers})

@login_required
def new_printer(request):
    form = PrinterForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            printer = form.save(commit=False)
            printer.user = request.user
            printer.auth_token = hexlify(os.urandom(10)).decode()
            printer.save()
            return redirect('/printers/{}/#step-2'.format(printer.id))

    return render(request, 'printer_wizard.html', {'form': form})

@login_required
def edit_printer(request, pk):
    instance = get_printer_or_404(pk, request)
    if request.method == "POST":
        form = PrinterForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
        return render(request, 'printer_wizard.html', {'form': form})
    else:
        return render(request, 'printer_wizard.html', {'form': PrinterForm(instance=instance)})

@login_required
def delete_printer(request, pk=None):
    get_printer_or_404(pk, request).delete()
    return redirect('/printers/')

@login_required
def cancel_printer(request, pk):
    printer = get_printer_or_404(pk, request)
    printer.queue_octoprint_command('cancel', clear_alert=True)
    return render(request, 'printer_acted.html', {'printer': printer, 'action': 'cancel'})

@login_required
def resume_printer(request, pk):
    printer = get_printer_or_404(pk, request)
    if request.GET.get('mute_alert', None):
        printer.current_print_alert_muted = True
        printer.save()

    printer.queue_octoprint_command('restore_temps', clear_alert=True)
    printer.queue_octoprint_command('resume', clear_alert=True)

    return render(request, 'printer_acted.html', {'printer': printer, 'action': 'resume'})

def publictimelapse_list(request):
    timelapses_list = list(PublicTimelapse.objects.order_by('priority').values())

    page = request.GET.get('page', 1)
    paginator = Paginator(timelapses_list, 9)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'publictimelapse_list.html', dict(timelapses=page_obj.object_list, page_obj=page_obj))

def serve_jpg_file(request, file_path):
    with open(os.path.join(settings.MEDIA_ROOT, file_path), 'rb') as fh:
        return HttpResponse(fh, content_type='image/jpeg')

### helper methods ###

def get_printer_or_404(pk, request):
    return get_object_or_404(Printer, pk=pk, user=request.user)
