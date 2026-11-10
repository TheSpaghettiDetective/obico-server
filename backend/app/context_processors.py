import re
import logging
from django.utils import translation
from django.conf import settings

from lib.syndicate import brand_from_request, brand_settings


RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')

def additional_context_export(request):

    platform = request.GET.get('platform', None)      # Allow get parameter to override for debugging purpose
    if not platform:
        m = RE_TSD_APP_PLATFORM.match(request.headers.get('X-TSD-Platform', '') or request.headers.get('user-agent', ''))
        platform = m.groupdict()['platform'] if m else ''

    # Named 'syndicate' in the templates and the frontend, but it is the brand.
    brand = brand_from_request(request)
    syndicate_settings = dict(brand_settings(brand), name=brand)

    language = request.GET.get('lang') or request.META.get('HTTP_ACCEPT_LANGUAGE', 'en-US')


    return {
        'page_context': {
            'app_platform': platform,
            'syndicate': syndicate_settings,
            'language': language,
        }
    }


def additional_settings_export(request):
    settings_dict = {
        'TWILIO_COUNTRY_CODES': settings.TWILIO_COUNTRY_CODES,
    }

    return settings_dict