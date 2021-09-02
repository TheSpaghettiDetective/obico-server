import re
import logging

from django.conf import settings

RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')


def detect_app_platform(request):
    platform = request.GET.get('platform', None)      # Allow get parameter to override for debugging purpose
    if not platform:
        m = RE_TSD_APP_PLATFORM.match(request.META.get('HTTP_USER_AGENT', ''))
        platform = m.groupdict()['platform'] if m else ''
    return {
        'app_platform': dict(platform=platform)
    }


def additional_settings_export(request):
    return {
        'TWILIO_COUNTRY_CODES': settings.TWILIO_COUNTRY_CODES,
    }
