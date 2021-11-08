import os
from binascii import hexlify
import re

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from allauth.account.views import LoginView

from lib.view_helpers import get_print_or_404, get_printer_or_404, get_paginator, get_template_path

from app.models import (User, Printer, SharedResource, GCodeFile)
from app.forms import SocialAccountAwareLoginForm
from lib import channels
from lib.integrations.telegram_bot import bot_name, telegram_bot, telegram_send
from lib.file_storage import save_file_obj
from app.tasks import preprocess_timelapse
from lib import cache

from . import tunnel_views
from . import tunnelv2_views


def index(request):
    if request.user.is_authenticated:
        if hasattr(settings, 'ACCOUNT_SIGNUP_REDIRECT_URL') and \
                Printer.objects.filter(user=request.user).count() == 0:
            return redirect(settings.ACCOUNT_SIGNUP_REDIRECT_URL)
        else:
            return redirect('/printers/')
    else:
        return redirect('/accounts/login/')


class SocialAccountAwareLoginView(LoginView):
    form_class = SocialAccountAwareLoginForm


@login_required
def printers(request, template_name='printers.html'):
    return render(request, template_name)


@login_required
def edit_printer(request, pk, template_dir=None):
    if pk == 'wizard':
        return render(request, get_template_path('printer_wizard', template_dir))
    else:
        return render(request, get_template_path('printer_settings', template_dir))


@login_required
def delete_printer(request, pk=None):
    printer = get_printer_or_404(pk, request, with_archived=True)
    printer.delete()
    messages.success(request, f'{printer.name} has been deleted!')

    return redirect('/printers/')


@login_required
def cancel_print(request, pk):
    _print = get_print_or_404(pk, request)

    if _print.id != _print.printer.current_print_id:
        succeeded = False
    else:
        succeeded = _print.printer.cancel_print()

    return render(request, 'printer_acted.html', {'printer': _print.printer, 'action': 'cancel', 'succeeded': succeeded})


@login_required
def resume_print(request, pk):
    _print = get_print_or_404(pk, request)

    if _print.id != _print.printer.current_print_id:
        succeeded = False
    else:
        succeeded = _print.printer.resume_print(mute_alert=request.GET.get('mute_alert', False))

    return render(request, 'printer_acted.html', {'printer': _print.printer, 'action': 'resume', 'succeeded': succeeded})


def printer_shared(request, share_token=None):
    printer = get_object_or_404(Printer, sharedresource__share_token=share_token, user__is_pro=True)

    return render(request, 'printer_shared.html', {'share_token': share_token})


@login_required
def printer_control(request, pk):
    return render(request, 'printer_control.html')


# User preferences


@login_required
def user_preferences(request, template_dir=None):
    params = dict(telegram_bot_name=bot_name) if bot_name else dict()

    return render(request, get_template_path('user_preferences', template_dir), params)

@csrf_exempt
@login_required
def test_telegram(request):
    if request.method == 'POST':
        user = request.user
        bot = telegram_bot()

        if bot and user.telegram_chat_id:
            # errors throw
            telegram_send(
                bot.send_message,
                user.telegram_chat_id, 'Test from TSD', parse_mode='Markdown')

            return JsonResponse(dict(status='Ok'))

    return JsonResponse(dict(status='API error'), status=400)


def unsubscribe_email(request):
    unsub_token = request.GET['unsub_token']
    email_list = request.GET['list']
    user = get_object_or_404(User.objects, unsub_token=unsub_token)
    setattr(user, f'{email_list}_by_email', False)
    user.save()

    return render(request, 'unsubscribe_email.html', dict(email_list=email_list))

### Prints and public time lapse ###

@login_required
def prints(request, template_dir=None):
    return render(request, get_template_path('prints', template_dir))

@login_required
def print(request, pk):
    _print = get_print_or_404(pk, request)
    return render(request, 'print.html', {'print': _print})


@login_required
def upload_print(request):
    if request.method == 'POST':
        _, file_extension = os.path.splitext(request.FILES['file'].name)
        video_path = f'{request.user.id}/{str(timezone.now().timestamp())}{file_extension}'
        save_file_obj(f'uploaded/{video_path}', request.FILES['file'], settings.PICS_CONTAINER, long_term_storage=False)
        preprocess_timelapse.delay(request.user.id, video_path, request.FILES['file'].name)

        return JsonResponse(dict(status='Ok'))
    else:
        return render(request, 'upload_print.html')


@login_required
def print_shot_feedback(request, pk):
    _print = get_print_or_404(pk, request)
    return render(request, 'print_shot_feedback.html', {'object': _print})


### GCode File page ###


@login_required
def gcodes(request, template_dir=None):
    return render(request, get_template_path('gcode_files', template_dir))


@login_required
def upload_gcode_file(request):
    if request.method == 'POST':
        _, file_extension = os.path.splitext(request.FILES['file'].name)
        gcode_file = GCodeFile.objects.create(
            user=request.user,
            filename=request.FILES['file'].name,
            safe_filename=re.sub(r'[^\w\.]', '_', request.FILES['file'].name),
            num_bytes=request.FILES['file'].size,
        )
        _, ext_url = save_file_obj(f'{request.user.id}/{gcode_file.id}', request.FILES['file'], settings.GCODE_CONTAINER)
        gcode_file.url = ext_url
        gcode_file.save()

        return JsonResponse(dict(status='Ok'))
    else:
        return render(request, 'upload_print.html')

### Misc ####

# Was surprised to find there is no built-in way in django to serve uploaded files in both debug and production mode
def serve_jpg_file(request, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if not os.path.exists(full_path):
        raise Http404("Requested file does not exist")
    with open(full_path, 'rb') as fh:
        return HttpResponse(fh, content_type=('video/mp4' if file_path.endswith('.mp4') else 'image/jpeg'))


# Health check that touches DB and redis
def health_check(request):
    User.objects.all()[:1]
    cache.printer_pic_get(0)
    return HttpResponse('Okay')


@csrf_exempt
@login_required
def octoprint_http_tunnel(request, pk):
    # We need to catch the moment when tunnel page loads,
    # and redirect to v2 url if plugin version is compatible.
    if request.path == tunnel_views.URL_PREFIX.format(pk=pk) + '/':
        get_printer_or_404(pk, request)
        version = (
            cache.printer_settings_get(pk) or {}
        ).get('tsd_plugin_version', '')
        if tunnelv2_views.is_plugin_version_supported(version):
            return tunnelv2_views.redirect_to_tunnel_url(request, pk)
    return tunnel_views.octoprint_http_tunnel(request, pk)
