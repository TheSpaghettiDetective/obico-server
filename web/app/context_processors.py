import re
import logging

RE_TSD_APP_PLATFORM = re.compile(r'TSDApp-(?P<platform>\w+)')


def detect_app_platform(request):
    m = RE_TSD_APP_PLATFORM.match(request.META.get('HTTP_USER_AGENT', ''))
    return {
        'app_platform': dict(platform=(m.groupdict()['platform'] if m else ''))
    }
