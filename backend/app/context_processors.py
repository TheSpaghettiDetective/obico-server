import re
import logging
from django.utils import translation
from django.conf import settings

from lib.syndicate import syndicate_from_request, settings_for_syndicate


RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')

def additional_context_export(request):

    platform = request.GET.get('platform', None)      # Allow get parameter to override for debugging purpose
    if not platform:
        m = RE_TSD_APP_PLATFORM.match(request.headers.get('X-TSD-Platform', '') or request.headers.get('user-agent', ''))
        platform = m.groupdict()['platform'] if m else ''

    # TODO: JusPrin syndicate hack so that we can set branding without add a syndicate to the DB
    user_agent = request.META.get('HTTP_USER_AGENT', 'Not provided')
    if user_agent.startswith("JusPrin"):
        syndicate_name = 'jusprin'
    else:
        syndicate_name = syndicate_from_request(request).name

    syndicate_settings = settings_for_syndicate(syndicate_name)
    syndicate_settings['name'] = syndicate_name

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