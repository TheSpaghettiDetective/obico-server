import os
from binascii import hexlify
import tempfile
import re
import time
import json
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

from .view_helpers import get_print_or_404, get_printer_or_404, get_paginator
from .models import (User, Printer, SharedResource, PublicTimelapse, GCodeFile)

from .forms import PrinterForm, UserPreferencesForm
from lib import redis
from lib import channels
from lib.integrations.telegram_bot import bot_name, telegram_bot
from lib.file_storage import save_file_obj
from app.tasks import preprocess_timelapse


def index(request):
    if request.user.is_authenticated and not request.user.consented_at:
        return redirect('/consent/')
    else:
        return redirect('/printers/')


@login_required
def printer_auth_token(request, pk):
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
    if not request.user.consented_at:
        return redirect('/consent/')

    return render(request, 'printers.html')


@login_required
def edit_printer(request, pk):
    if pk == 'new':
        printer = None
        template = 'printer_wizard.html'
    else:
        printer = get_printer_or_404(int(pk), request)
        template = 'printer_wizard.html' if request.GET.get('wizard', False) else 'edit_printer.html'

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
    printer = get_printer_or_404(pk, request)
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


@login_required
def share_printer(request, pk):
    printer = get_printer_or_404(pk, request)

    if request.method == "POST":
        if request.POST.get('shared') == 'on':
            if not hasattr(printer, 'sharedresource'):
                SharedResource.objects.create(printer=printer, share_token=hexlify(os.urandom(18)).decode())
        else:
            SharedResource.objects.filter(printer=printer).delete()
            messages.success(request, 'You have disabled printer feed sharing. Previous shareable link has now been revoked.')

    return render(request, 'share_printer.html', dict(printer=printer, user=request.user))


def printer_shared(request, share_token=None):
    printer = get_object_or_404(Printer, sharedresource__share_token=share_token, user__is_pro=True)

    return render(request, 'printer_shared.html', {'share_token': share_token})


@login_required
def control_printer(request, pk):
    return render(request, 'printer_control.html', {'printer': get_printer_or_404(pk, request)})


@login_required
def integration(request, pk):
    printer = get_printer_or_404(pk, request)
    if request.method == "POST":
        if request.POST.get('enable') == 't' and not printer.service_token:
            printer.service_token = hexlify(os.urandom(24)).decode()
            printer.save()
        elif request.POST.get('enable') == 'f':
            printer.service_token = None
            printer.save()
            messages.success(request, "3D Geeks integration has been turned off successfully.")

    return render(request, 'printer_integration.html', {'printer': printer})

# User preferences


@login_required
def user_preferences(request):
    form = UserPreferencesForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Your preferences have been updated successfully!')

    return render(request, 'user_preferences.html', dict(form=form, bot_name=bot_name))


@login_required
def test_telegram(request):
    if request.method == 'POST':
        user = request.user
        bot = telegram_bot()

        if bot and user.telegram_chat_id:
            bot.send_message(user.telegram_chat_id, 'Test from TSD', parse_mode='Markdown')  # errors throw

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
def prints(request):
    return render(request, 'prints.html')


@login_required
def print(request, pk):
    _print = get_print_or_404(pk, request)
    return render(request, 'print.html', {'object': _print})


@login_required
def upload_print(request):
    if request.method == 'POST':
        _, file_extension = os.path.splitext(request.FILES['file'].name)
        video_path = f'{str(timezone.now().timestamp())}{file_extension}'
        save_file_obj(f'uploaded/{video_path}', request.FILES['file'], settings.TIMELAPSE_CONTAINER)
        preprocess_timelapse.delay(request.user.id, video_path, request.FILES['file'].name)

        return JsonResponse(dict(status='Ok'))
    else:
        return render(request, 'upload_print.html')


@login_required
def print_shot_feedback(request, pk):
    _print = get_print_or_404(pk, request)
    return render(request, 'print_shot_feedback.html', {'object': _print})


def publictimelapse_list(request):
    timelapses_list = list(PublicTimelapse.objects.order_by('priority').values())
    page_obj = get_paginator(timelapses_list, request, 9)

    return render(request, 'publictimelapse_list.html', dict(timelapses=page_obj.object_list, page_obj=page_obj))


### Consent page #####

@login_required
def consent(request):
    if request.method == 'POST':
        user = request.user
        user.consented_at = timezone.now()
        user.save()

        return redirect('/printers/')
    else:
        return render(request, 'consent.html')

### GCode File page ###


@login_required
def gcodes(request):
    gcodes = GCodeFile.objects.filter(user=request.user)

    return render(request, 'gcode_files.html', dict(gcodes=gcodes))


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


def secure_redirect(request):
    target = request.GET.get('target')
    source = request.GET.get('source')
    dest = settings.SECURE_REDIRECTS.get((target, source), target)

    return redirect(dest)


### Proxy for OctoPrint ####

@csrf_exempt
@login_required
def octoprint_http_proxy(request, printer_id):
    get_printer_or_404(printer_id, request)

    prefix = f'/octoprint/{printer_id}'  # FIXME
    method = request.method.lower()
    path = request.get_full_path()[len(prefix):]

    IGNORE_HEADERS = [
        'HTTP_HOST', 'HTTP_ORIGIN', 'HTTP_REFERER', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED_HOST', 'HTTP_X_FORWARDED_PORT', 'HTTP_X_FORWARDED_PROTO'
    ]

    # Recreate http headers, because django put headers in request.META as "HTTP_XXX_XXX". Is there a better way?
    headers = {
        k[5:].replace("_", " ").title().replace(" ", "-"): v
        for (k, v) in request.META.items()
        if k.startswith("HTTP") and k not in IGNORE_HEADERS
    }

    if 'CONTENT_TYPE' in request.META:
        headers['Content-Type'] = request.META['CONTENT_TYPE']

    ref = f'{printer_id}.{method}.{time.time()}.{path}'

    channels.send_msg_to_printer(
        printer_id,
        {
            "http.proxy": {
                "ref": ref,
                "method": method,
                "headers": headers,
                "path": path,
                "data": request.body
            }
        },
        as_binary=True)

    data = redis.octoprintproxy_http_response_get(ref)
    if data is None:
        raise Exception(f'no response in time: {path}')

    content_type = data['response']['headers'].get('Content-Type') or None
    resp = HttpResponse(
        status=data["response"]["status"],
        content_type=content_type,
    )
    for k, v in data['response']['headers'].items():
        if k == 'Content-Length':
            continue
        resp[k] = v

    content = data['response']['content']
    if content_type and content_type.startswith('text/html'):
        content = rewrite_html(prefix, ensure_bytes(content))
    elif path.endswith('app/client/socket.js'):
        content = rewrite_socket_js(ensure_bytes(content))
    elif path.endswith('sockjs.js'):
        content = rewrite_sockjs_js(ensure_bytes(content))
    elif path.endswith('sockjs.min.js'):
        content = rewrite_sockjs_min_js(ensure_bytes(content))

    resp.write(content)

    return resp


def ensure_bytes(content):
    # If plugin side runs on py2.7
    # then content is potentially a string.
    # Rewriting later expects bytes.
    if not isinstance(content, bytes):
        return content.encode()
    return content


def rewrite_socket_js(content):
    # force websocket-only connection
    # xhr(-streams/etc) won't work for now
    return content.replace(
        b'OctoPrintSocketClient.prototype.connect = function(opts) {',
        b'OctoPrintSocketClient.prototype.connect = function(opts) {\nopts = opts || {}; opts["transports"] = ["websocket", ];\n'  # noqa
    )


def rewrite_sockjs_js(content):
    # Route sockjs to "^/ws/" as Ops requires all websocket path starts with "/ws"
    return content.replace(
        b"urlUtils.addPath(transUrl, '/websocket')",
        b"urlUtils.addPath(transUrl.replace('/octoprint', '/ws/octoprint'), '/websocket')"
    )


def rewrite_sockjs_min_js(content):
    # Route sockjs to "^/ws/" as Ops requires all websocket path starts with "/ws"
    return content.replace(
        b'addPath(t,"/websocket")',
        b'addPath(t.replace("/octoprint", "/ws/octoprint"),"/websocket")'
    )


def rewrite_html(prefix, content):
    # rewirte urls
    return content\
        .replace(b'src="/',
                 f'src="{prefix}/'.encode())\
        .replace(b'href="/',
                 f'href="{prefix}/'.encode())\
        .replace(b'var BASEURL = "/',
                 f'var BASEURL = "{prefix}'.encode())\
        .replace(b'var GCODE_WORKER = "/',
                 f'var GCODE_WORKER = "{prefix}'.encode())
