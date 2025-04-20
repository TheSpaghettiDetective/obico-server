import mimetypes
import os
from binascii import hexlify
import re
from wsgiref.util import FileWrapper

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, StreamingHttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
import json
from django.utils.translation import gettext_lazy as _
from allauth.account.views import LoginView, SignupView, PasswordResetView

from lib.url_signing import HmacSignedUrl
from lib.view_helpers import get_print_or_404, get_printer_or_404, get_paginator, get_template_path
from app.models import (User, Printer, SharedResource, GCodeFile, NotificationSetting)
from app.forms import SocialAccountAwareLoginForm
from lib import channels
from lib.file_storage import save_file_obj
from app.tasks import preprocess_timelapse
from lib import cache
from lib.syndicate import syndicate_from_request
from allauth.account.views import EmailView

from app.forms import SyndicateSpecificResetPasswordForm
from app.forms import SyndicateSpecificAddEmailForm



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

class SocialAccountAwareSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        if settings.ACCOUNT_ALLOW_SIGN_UP:
            return super().dispatch(request, *args, **kwargs)
        return redirect('/accounts/login/')
    def form_valid(self, form):
            email = form.cleaned_data['email']
            syndicate = syndicate_from_request(self.request)
            if User.objects.filter(emailaddress__email__iexact=email, syndicate=syndicate).exists():
                form.add_error('email', _('A user is already registered with this email address.'))
                return self.form_invalid(form)
            return super(SocialAccountAwareSignupView, self).form_valid(form)


class SyndicateSpecificEmailView(EmailView):
    form_class = SyndicateSpecificAddEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SyndicateSpecificPasswordResetView(PasswordResetView):
    form_class = SyndicateSpecificResetPasswordForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

@login_required
def printers(request, template_name='printers.html'):
    return render(request, template_name)


@login_required
def new_printer(request, route=None, template_dir=None):
    return render(request, get_template_path('printer_wizard', template_dir))

@login_required
def edit_printer(request, pk, template_dir=None):
    return render(request, get_template_path('printer_settings', template_dir))


# TODO: Deprecated in favor the REST API call. Remove when calls from the Mobile app is all gone.
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


@xframe_options_exempt
def printer_shared(request, share_token=None):
    printer = get_object_or_404(Printer, sharedresource__share_token=share_token, user__is_pro=True)

    return render(request, 'printer_shared.html', {'share_token': share_token})


@login_required
def printer_control(request, pk):
    return render(request, 'printer_control.html')

@login_required
def printer_terminal(request, pk):
    return render(request, 'printer_terminal.html')


# User preferences

@login_required
def user_preferences(request, route=None, template_dir=None):
    return render(request, get_template_path('user_preferences', template_dir))


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
        config_json=json.dumps({'access_token': r.json().get('access_token')})
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
        nsetting.notify_on_heater_status = False
        nsetting.notify_on_print_start = False
        nsetting.notify_on_print_pause = False
        nsetting.notify_on_print_resume = False
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
def print_history(request, template_dir=None):
    return render(request, get_template_path('print_history', template_dir))

@login_required
def stats(request, template_dir=None):
    return render(request, get_template_path('stats', template_dir))

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
        save_file_obj(f'uploaded/{video_path}', request.FILES['file'], settings.TIMELAPSE_CONTAINER, request.user.syndicate.name, long_term_storage=True)
        preprocess_timelapse.delay(request.user.id, video_path, request.FILES['file'].name)

        return JsonResponse(dict(status='Ok'))
    else:
        return render(request, 'upload_print.html')


@login_required
def print_shot_feedback(request, pk):
    _print = get_print_or_404(pk, request)
    return render(request, 'print_shot_feedback.html', {'object': _print})


@login_required
def g_code_folders(request, template_dir=None):
    return render(request, get_template_path('g_code_folders', template_dir))


@login_required
def g_code_files(request, template_dir=None):
    return render(request, get_template_path('g_code_files', template_dir))


@login_required
def printer_events(request):
    user = request.user
    user.unseen_printer_events = 0
    user.save()
    return render(request, 'printer_events.html')


@login_required
def first_layer_inspection_images(request):
    return render(request, 'first_layer_inspection_images.html')


### Misc ####

# Was surprised to find there is no built-in way in django to serve uploaded files in both debug and production mode

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
def serve_jpg_file(request, file_path):
    url = HmacSignedUrl(request.get_full_path())
    if not url.is_authorized():
        return HttpResponseForbidden("You do not have permission to view this media")
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    # Determine content type based on file extension
    content_type = mimetypes.guess_type(file_path)[0]
    # Content type is not guessed correctly for files without extensions (i.e. for gcode files), so we set the
    # content_type to octet-stream, which initiates a download in the user's browser.
    if content_type is None:
        content_type = "application/octet-stream"
    if not os.path.exists(full_path):
        raise Http404("Requested file does not exist")

    fh = open(full_path, 'rb')
    try:
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        size = os.path.getsize(full_path)

        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(RangeFileWrapper(fh, offset=first_byte, length=length), status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            resp = StreamingHttpResponse(FileWrapper(fh), content_type=content_type)
            resp['Content-Length'] = str(size)

        resp['Accept-Ranges'] = 'bytes'
        return resp
    except:
        pass

# Health check that touches DB and redis
def health_check(request):
    User.objects.all()[:1]
    cache.printer_pic_get(0)
    return HttpResponse('Okay')

def orca_slicer_authorized(request):
    access_granted = 'true' if request.GET.get('error') != 'access_denied' else 'false'
    return render(request, 'orca_slicer_authorized.html', {'access_granted': access_granted})
