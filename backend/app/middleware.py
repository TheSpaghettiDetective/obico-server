from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
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

from app.models import User
from django.contrib.auth import login as auth_login
from oauth2_provider.models import AccessToken
from oauth2_provider.signals import app_authorized

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
            now_ts = int(time.time())
            expires_at_ts = session.get('_session_expire_at_ts', None)
            refresh_at_ts = expires_at_ts or now_ts - (settings.SESSION_COOKIE_AGE - settings.SESSION_COOKIE_REFRESH_INTERVAL)
            if expires_at_ts is None or now_ts >= refresh_at_ts:
                # This will set modified flag and update the cookie expiration time
                session['_session_expire_at_ts'] = now_ts + settings.SESSION_COOKIE_AGE
        response = super().process_response(request, response)
        # If setting a session cookie, ensure we set the domain attribute so that the cookie
        # passes through to subdomains for tunneling
        if response.cookies:
            # Only update domain of our session cookie if domain is not set.
            # Does nothing if settings.SESSION_COOKIE_DOMAIN is configured.
            session_cookie = response.cookies.get(settings.SESSION_COOKIE_NAME, None)
            if session_cookie and not session_cookie.get('domain', ''):
                session_cookie['domain'] = str(request.get_host()).split(':')[0]
        return response


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

def authenticate_credentials(key):
    try:
        access_token = AccessToken.objects.get(token=key)
        if access_token.is_valid():
            user = access_token.user
            return user
        else:
            return None  # Token is expired or invalid
    except AccessToken.DoesNotExist:
        return None  # Token does not exist


# HTTP_X_API_KEY seems to be needed by OrcaSlicer: https://github.com/TheSpaghettiDetective/OrcaSlicer/blob/5a0f98e3f2634a61d8ad2f3b78bebf8e38f19de7/src/slic3r/GUI/PrinterWebView.cpp#L108
# But I'm not too sure if it's really needed. I'll leave it here for now.

def check_x_api(get_response):
    def middleware(request):
        token = request.META.get('HTTP_X_API_KEY', '')
        if token:
            user = authenticate_credentials(token)
            request.user = user
            setattr(request.user, 'backend', 'django.contrib.auth.backends.ModelBackend')
            auth_login(request, request.user)

        response = get_response(request)
        return response


    return middleware