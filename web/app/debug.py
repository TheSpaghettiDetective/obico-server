from rest_framework.views import exception_handler
from raven.contrib.django.raven_compat.models import client as sentryClient
import sys

from .context_processors import RE_TSD_APP_PLATFORM


def custom_exception_handler(exc, context):
    if context and 'request' in context:
        m = RE_TSD_APP_PLATFORM.match(
            context['request'].META.get('HTTP_USER_AGENT', ''))
        if m:
            sentryClient.captureException(exc_info=sys.exc_info())
    response = exception_handler(exc, context)
    return response
