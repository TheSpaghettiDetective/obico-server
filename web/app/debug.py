from rest_framework.views import exception_handler
from raven.contrib.django.raven_compat.models import client as sentryClient
import sys
import re

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
            sentryClient.captureException(exc_info=sys.exc_info())
    response = exception_handler(exc, context)
    return response
