from django.conf import settings
from django.core.exceptions import SuspiciousOperation, MiddlewareNotUsed, PermissionDenied
from django.contrib.sessions.backends.base import UpdateError

from whitenoise.middleware import WhiteNoiseMiddleware
import time
from django.utils.cache import patch_vary_headers
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.http import http_date
from django.urls import reverse, NoReverseMatch

from ipware import get_client_ip

from .views import tunnelv2_views
from lib.tunnelv2 import OctoprintTunnelV2Helper

import logging

LOGGER = logging.getLogger()

class TSDWhiteNoiseMiddleware(WhiteNoiseMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        path = settings.WELL_KNOWN_PATH
        if path:
            self.add_files(path, prefix="/.well-known")

    def get_response(self, request):
        if OctoprintTunnelV2Helper.is_tunnel_request(request):
            return None

        return super().get_response(request)


def octoprint_tunnelv2(get_response):

    def middleware(request):
        if OctoprintTunnelV2Helper.is_tunnel_request(request):
            return tunnelv2_views.octoprint_http_tunnel(request)

        response = get_response(request)
        return response

    return middleware


def fix_tunnelv2_apple_cache(get_response):
    # necessary to make caching in ios webviews and safari work

    def middleware(request):
        resp = get_response(request)

        if (
            getattr(resp, '_from_tunnelv2', False) and
            '/static/' in request.get_full_path()
        ):
            for k in list(resp.cookies.keys()):
                del resp.cookies[k]

            if resp.has_header('Vary'):
                del resp['Vary']

        return resp

    return middleware

# https://stackoverflow.com/questions/64466605/django-how-to-get-the-time-until-a-cookie-expires
class RefreshSessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        session = request.session
        if not (session.is_empty() or session.get_expire_at_browser_close()):
            expires_at_ts = session.get('_session_expire_at_ts', None)
            now_ts = int(time.time())
            refresh_at_ts = expires_at_ts - (settings.SESSION_COOKIE_AGE - settings.SESSION_COOKIE_REFRESH_INTERVAL)
            if expires_at_ts is None or now_ts >= refresh_at_ts:
                # This will set modified flag and update the cookie expiration time
                session['_session_expire_at_ts'] = now_ts + settings.SESSION_COOKIE_AGE
        return super().process_response(request, response)


def check_admin_ip_whitelist(get_response):
    try:
        prefix = reverse('admin:index')
    except NoReverseMatch:
        logging.error('admin site is not installed - ip whitelisting is disabled')
        raise MiddlewareNotUsed

    def middleware(request):
        if request.path.startswith(prefix) and settings.ADMIN_IP_WHITELIST:
            client_ip, is_routable = get_client_ip(request)
            if client_ip not in settings.ADMIN_IP_WHITELIST:
                raise PermissionDenied()

        response = get_response(request)
        return response

    return middleware
