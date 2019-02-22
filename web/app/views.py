import os
from binascii import hexlify
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings

from .models import *
from .forms import *

if settings.TWILIO_API_KEY:
    authy_api = AuthyApiClient(settings.TWILIO_API_KEY)

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
    printer.cancel_print()
    return render(request, 'printer_acted.html', {'printer': printer, 'action': 'cancel'})

@login_required
def resume_printer(request, pk):
    printer = get_printer_or_404(pk, request)
    printer.resume_print(mute_alert=request.GET.get('mute_alert', False))
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

# User preferences

@login_required
def user_preferences(request):
    form = UserPrefernecesForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your preferences have been updated successfully!')

    return render(request, 'user_preferences.html', dict(form=form))

@login_required
def phone_verification(request):
    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            request.session['phone_number'] = form.cleaned_data['phone_number']
            request.session['country_code'] = form.cleaned_data['country_code']
            authy_api.phones.verification_start(
                form.cleaned_data['phone_number'],
                form.cleaned_data['country_code'],
                via=form.cleaned_data['via']
            )
            return redirect('phone_token_validation')
    else:
        form = PhoneVerificationForm(initial={'via': 'sms'})
    return render(request, 'phone_verification.html', {'form': form})

@login_required
def phone_token_validation(request):
    if request.method == 'POST':
        form = PhoneTokenForm(request.POST)
        if form.is_valid():
            verification = authy_api.phones.verification_check(
                request.session['phone_number'],
                request.session['country_code'],
                form.cleaned_data['token']
            )
            if verification.ok():
                request.session['is_verified'] = True
                request.user.phone_country_code = request.session['country_code']
                request.user.phone_number = request.session['phone_number']
                request.user.save()
                messages.success(request, 'Phone number has been verified successfully!')
                return redirect('user_preferences')
            else:
                for error_msg in verification.errors().values():
                    form.add_error(None, error_msg)
    else:
        form = PhoneTokenForm()
    return render(request, 'phone_token_validation.html', {'form': form})


### helper methods ###

def get_printer_or_404(pk, request):
    return get_object_or_404(Printer, pk=pk, user=request.user)
