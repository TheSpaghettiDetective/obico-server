from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.models import *

def get_printer_or_404(pk, request):
    return get_object_or_404(Printer.with_archived, pk=pk, user=request.user)

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
    return get_object_or_404(Print, pk=pk, user=request.user)
