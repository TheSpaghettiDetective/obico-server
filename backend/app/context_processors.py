import re
import logging
from django.utils import translation
from django.conf import settings

from lib.syndicate import syndicate_from_request, settings_for_syndicate
from lib.turn import turn_config
from app.models import SharedResource


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

    syndicate_settings = dict(settings_for_syndicate(syndicate_name), name=syndicate_name)

    # TURN credentials only go to pages that can stream a webcam. Login and other public pages must not carry them.
    if request.user.is_authenticated:
        syndicate_settings['turn'] = turn_config(label=f'user-{request.user.id}', ttl_seconds=settings.TURN_WEB_CREDENTIAL_TTL)
    elif is_valid_shared_printer_page(request):
        syndicate_settings['turn'] = turn_config(label='share', ttl_seconds=settings.TURN_WEB_CREDENTIAL_TTL)

    language = request.GET.get('lang') or request.META.get('HTTP_ACCEPT_LANGUAGE', 'en-US')


    return {
        'page_context': {
            'app_platform': platform,
            'syndicate': syndicate_settings,
            'language': language,
        }
    }


def is_valid_shared_printer_page(request):
    match = request.resolver_match
    if not match or match.url_name != 'printer_shared':
        return False
    return SharedResource.objects.filter(share_token=match.kwargs.get('share_token'), printer__user__is_pro=True).exists()


def additional_settings_export(request):
    settings_dict = {
        'TWILIO_COUNTRY_CODES': settings.TWILIO_COUNTRY_CODES,
    }

    return settings_dict