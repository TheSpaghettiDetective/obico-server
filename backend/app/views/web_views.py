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
import requests

from allauth.account.views import LoginView

from lib.view_helpers import get_print_or_404, get_printer_or_404, get_paginator, get_template_path

from app.models import (User, Printer, SharedResource, GCodeFile, NotificationSetting)
from app.forms import SocialAccountAwareLoginForm
from lib import channels
from lib.integrations.telegram_bot import bot_name, telegram_bot, telegram_send
from lib.file_storage import save_file_obj
from app.tasks import preprocess_timelapse
from lib import cache


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
def new_printer(request, route=None, template_dir=None):
    return render(request, get_template_path('printer_wizard', template_dir))

@login_required
def edit_printer(request, pk, template_dir=None):
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
        succeeded = _print.printer.cancel_print(initiator='web')

    return render(request, 'printer_acted.html', {'printer': _print.printer, 'action': 'cancel', 'succeeded': succeeded})


@login_required
def resume_print(request, pk):
    _print = get_print_or_404(pk, request)

    if _print.id != _print.printer.current_print_id:
        succeeded = False
    else:
        succeeded = _print.printer.resume_print(mute_alert=request.GET.get('mute_alert', False), initiator='web')

    return render(request, 'printer_acted.html', {'printer': _print.printer, 'action': 'resume', 'succeeded': succeeded})


def printer_shared(request, share_token=None):
    printer = get_object_or_404(Printer, sharedresource__share_token=share_token, user__is_pro=True)

    return render(request, 'printer_shared.html', {'share_token': share_token})


@login_required
def printer_control(request, pk):
    return render(request, 'printer_control.html')


# User preferences


@login_required
def user_preferences(request, route=None, template_dir=None):
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
                user.telegram_chat_id, 'Test from Obico', parse_mode='Markdown')

            return JsonResponse(dict(status='Ok'))

    return JsonResponse(dict(status='API error'), status=400)

@csrf_exempt
@login_required
def test_slack(request):
    if request.method == 'POST':
        user = request.user
        if user.slack_access_token:
            req = requests.get(
            url='https://slack.com/api/conversations.list',
            headers={'Authorization': f'Bearer {user.slack_access_token}'},
            params={
                'types': 'public_channel,private_channel'
            })
        req.raise_for_status()
        slack_channel_ids = [c['id'] for c in req.json().get('channels') or [] if c['is_member']]
        for slack_channel_id in slack_channel_ids:
            msg = {
                "channel": slack_channel_id,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Test from TSD"
                        }
                    }
                ]
            }

            req = requests.post(
                url='https://slack.com/api/chat.postMessage',
                headers={'Authorization': f'Bearer {user.slack_access_token}'},
                json=msg
            )
            req.raise_for_status()

            return JsonResponse(dict(status='Ok'))

    return JsonResponse(dict(status='API error'), status=400)


# Slack setup callback
@login_required
def slack_oauth_callback(request):
    from notifications.plugins.slack import slack_client_id
    code = request.GET['code']
    r = requests.post(
        url='https://slack.com/api/oauth.v2.access',
        data={
            'code': code,
            'client_id': slack_client_id(),
            'client_secret': os.environ.get('SLACK_CLIENT_SECRET'),
            'redirect_uri': request.build_absolute_uri(''),
        })
    r.raise_for_status()

    NotificationSetting.objects.create(
        user=request.user,
        name='slack',
        config={'access_token': r.json().get('access_token')}
    )
    return redirect('/user_preferences/notification_slack/')


def unsubscribe_email(request):
    unsub_token = request.GET.get('unsub_token')
    email_list = request.GET.get('list')
    if not unsub_token or not email_list:
        raise Http404("Request object not found")

    user = get_object_or_404(User.objects, unsub_token=unsub_token)
    nsetting = NotificationSetting.objects.get(user_id=user.id, name='email')
    if email_list == 'alert':
        # FIXME added to support emails already sent
        # can be removed later
        nsetting.notify_on_failure_alert = False
        nsetting.save()
    elif email_list == 'print_notification':
        # FIXME added to support emails already sent
        # can be removed later
        nsetting.notify_on_print_done = False
        nsetting.notify_on_print_cancelled = False
        nsetting.notify_on_filament_change = False
        nsetting.notify_on_other_print_events = False
        nsetting.notify_on_heater_status = False
        nsetting.save()
    elif email_list == 'account_notification':
        user.account_notification_by_email = False
        user.save()
    else:
        # let's not fail silently on unexpected email_list param
        # this raises FieldDoesNotExist
        nsetting._meta.get_field(f'notify_on_{email_list}')

        setattr(nsetting, f'notify_on_{email_list}', False)
        nsetting.save()

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
