import re
import logging

from django.conf import settings

RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')


def detect_app_platform(request):
    platform = request.GET.get('platform', None)      # Allow get parameter to override for debugging purpose
    if not platform:
        m = RE_TSD_APP_PLATFORM.match(request.headers.get('user-agent', ''))
        platform = m.groupdict()['platform'] if m else ''
    return {
        'app_platform': dict(platform=platform)
    }


def additional_settings_export(request):
    settings_dict = {
        'TWILIO_COUNTRY_CODES': settings.TWILIO_COUNTRY_CODES,
    }

    syndicate = settings.SYNDICATE

    # per-request syndicate overrides the global setting. This is so that Mintion users can use Obico cloud but see their own theme.
    syndicate_header = request.META.get('HTTP_X_OBICO_SYNDICATE', None)
    if syndicate_header:
        syndicate = syndicate_header

    brand_name = "Obico" if syndicate == "base" else syndicate.capitalize()
    settings_dict["syndicate"] = {"provider": syndicate, "brand_name": brand_name}

    accept_language_header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    languages = accept_language_header.split(",")
    if languages:
        brower_language = languages[0].split("-")[0]
        settings_dict["language"] = {"provider": brower_language}

    return settings_dict