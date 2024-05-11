import re
import logging
from django.utils import translation
from django.conf import settings

from lib.syndicate import syndicate_from_request


RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')

def additional_context_export(request):

    platform = request.GET.get('platform', None)      # Allow get parameter to override for debugging purpose
    if not platform:
        m = RE_TSD_APP_PLATFORM.match(request.headers.get('user-agent', ''))
        platform = m.groupdict()['platform'] if m else ''

    syndicate = syndicate_from_request(request).name

    brand_name = "Obico" if syndicate == "base" else syndicate.capitalize()

    language = translation.get_language_from_request(request).split('-')[0] # ISO 639-1 standard is language_code-country_code
    return {
        'page_context': {
            'app_platform': platform,
            'syndicate': {"provider": syndicate, "brand_name": brand_name},
            'language': language,
        }
    }


def additional_settings_export(request):
    settings_dict = {
        'TWILIO_COUNTRY_CODES': settings.TWILIO_COUNTRY_CODES,
    }

    return settings_dict