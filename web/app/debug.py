from rest_framework.views import exception_handler
from raven.contrib.django.raven_compat.models import client as sentryClient
import sys
import re

from django.contrib.sessions.models import Session
from django.forms import model_to_dict

RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)|TSDApp|;\ wv\)')

TO_APP_PLATFORM = {
    # before v1.26/39 user agent was not explicitely set in TSD app
    # on ios TSDApp substring has been present, on android we have only "wv" (webview) as a tip
    'TSDApp': 'ios',
    'TSDApp-ios': 'ios',
    'TSDApp-android': 'android',
    '; wv)': 'android',
}


def get_app_platform(user_agent):
    m = RE_TSD_APP_PLATFORM.search(user_agent)
    return TO_APP_PLATFORM.get(m.group() if m else None, '')


def custom_exception_handler(exc, context):
    if context and 'request' in context:
        if get_app_platform(context['request'].META.get('HTTP_USER_AGENT', '')):
            extra = {'session_key': 'nocookie'}
            if context['request'].COOKIES.get('sessionid'):
                sess = Session.objects.filter(session_key=context['request'].COOKIES['sessionid']).first()
                extra = model_to_dict(sess) if sess else {'session_key': 'doesnotexist'}

            sentryClient.captureException(exc_info=sys.exc_info(), extra=extra)
    response = exception_handler(exc, context)
    return response
