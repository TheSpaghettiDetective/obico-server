import os
from binascii import hexlify
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.http import Http404

from .models import *
from .forms import *
from lib import redis
from lib.channels import send_commands_to_group

# Create your views here.
def index(request):
    return redirect('/printers/')

@login_required
def priner_auth_token(request, pk):
    pk_filter = {}
    if pk != 0:
        pk_filter = dict(pk=pk)
    printers = Printer.objects.filter(user=request.user, **pk_filter)

    if printers.count() == 0:
        messages.error(request, 'You need to add a printer to get its secret token.')
        return redirect(reverse('printers'))

    return render(request, 'printer_auth_token.html', {'printers': printers})

@login_required
def printers(request):
    printers = Printer.objects.filter(user=request.user)
    for printer in printers:
        p_settings = redis.printer_settings_get(printer.id)
        printer.settings = dict((key, p_settings.get(key, 'False') == 'True') for key in ('webcam_flipV', 'webcam_flipH', 'webcam_rotate90'))

    return render(request, 'printer_list.html', {'printers': printers})

@login_required
def edit_printer(request, pk):
    if pk == 'new':
        printer = None
        template = 'printer_wizard.html'
    else:
        printer = get_printer_or_404(int(pk), request)
        template = 'printer_wizard.html' if request.GET.get('wizard', False) else 'printer_edit.html'

    form = PrinterForm(request.POST or None, request.FILES or None, instance=printer)
    if request.method == "POST":
        if form.is_valid():
            if pk == 'new':
                printer = form.save(commit=False)
                printer.user = request.user
                printer.auth_token = hexlify(os.urandom(10)).decode()
                form.save()
                return redirect('/printers/{}/?wizard=True#step-2'.format(printer.id))
            else:
                form.save()
                if not request.GET.get('wizard', False):
                    messages.success(request, 'Printer settings have been updated successfully!')

    return render(request, template, {'form': form})

@login_required
def delete_printer(request, pk=None):
    get_printer_or_404(pk, request).delete()
    return redirect('/printers/')

@login_required
def cancel_printer(request, pk):
    printer = get_printer_or_404(pk, request)
    printer.cancel_print()
    send_commands_to_group(printer.id)
    return render(request, 'printer_acted.html', {'printer': printer, 'action': 'cancel'})

@login_required
def resume_printer(request, pk):
    printer = get_printer_or_404(pk, request)
    printer.resume_print(mute_alert=request.GET.get('mute_alert', False))
    send_commands_to_group(printer.id)
    return render(request, 'printer_acted.html', {'printer': printer, 'action': 'resume'})


# User preferences

@login_required
def user_preferences(request):
    form = UserPrefernecesForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your preferences have been updated successfully!')

    return render(request, 'user_preferences.html', dict(form=form))

### Prints and public time lapse ###

@login_required
def prints(request):
    prints = get_prints(request).filter(prediction_json_url__isnull=False).order_by('-id')
    page_obj = get_paginator(prints, request, 9)
    prediction_urls = [ dict(print_id=print.id, prediction_json_url=print.prediction_json_url) for print in page_obj.object_list]
    return render(request, 'print_list.html', dict(prints=page_obj.object_list, page_obj=page_obj, prediction_urls=prediction_urls))

@login_required
def delete_prints(request, pk):
    if request.method == 'POST':
        select_prints_ids = request.POST.getlist('selected_print_ids', [])
    else:
        select_prints_ids = [pk]

    get_prints(request).filter(id__in=select_prints_ids).delete()
    messages.success(request, '{} time-lapses deleted.'.format(len(select_prints_ids)))
    return redirect(reverse('prints'))

def publictimelapse_list(request):
    timelapses_list = list(PublicTimelapse.objects.order_by('priority').values())
    page_obj = get_paginator(timelapses_list, request, 9)
    return render(request, 'publictimelapse_list.html', dict(timelapses=page_obj.object_list, page_obj=page_obj))


# Was surprised to find there is no built-in way in django to serve uploaded files in both debug and production mode

def serve_jpg_file(request, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if not os.path.exists(full_path):
        raise Http404("Requested file does not exist")
    with open(full_path, 'rb') as fh:
        return HttpResponse(fh, content_type='image/jpeg')


### helper methods ###

def get_printer_or_404(pk, request):
    return get_object_or_404(Printer, pk=pk, user=request.user)

def get_prints(request):
    return Print.objects.filter(printer__user=request.user)

def get_paginator(objs, request, num_per_page):
    page = request.GET.get('page', 1)
    paginator = Paginator(objs, num_per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj
