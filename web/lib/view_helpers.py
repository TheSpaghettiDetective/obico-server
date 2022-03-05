from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now

from app.models import *

def get_printer_or_404(pk, request, with_archived=False):
    obj_filter = Printer.with_archived if with_archived else Printer.objects
    return get_object_or_404(obj_filter, pk=pk, user=request.user)

def get_printers(request):
    return Printer.objects.filter(user=request.user)

def get_prints(request):
    return Print.objects.filter(user=request.user)

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

def get_print_or_404(pk, request):
    if not request.user.is_authenticated:
        raise PermissionDenied
    return get_object_or_404(Print, pk=pk, user=request.user)

def get_template_path(template_name, template_dir):
    return f"{template_dir + '/' if template_dir else ''}{template_name}.html"

def touch_user_last_active(user):
    user.last_active_at = now()
    user.save(update_fields=['last_active_at',])