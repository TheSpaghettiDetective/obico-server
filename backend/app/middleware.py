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


class TSDWhiteNoiseMiddleware(WhiteNoiseMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        path = settings.WELL_KNOWN_PATH
        if path:
            self.add_files(path, prefix="/.well-known")

    def process_request(self, request):
        if OctoprintTunnelV2Helper.is_tunnel_request(request):
            return None

        return super().process_request(request)


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


# https://stackoverflow.com/questions/2116860/django-session-cookie-domain-with-multiple-domains
# https://ittone.ma/ittone/django-session_cookie_domain-with-multiple-domains/
class SessionHostDomainMiddleware(SessionMiddleware):

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie or delete
        the session cookie if the session has been emptied.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            pass
        else:
            host = request.get_host().split(':')[0]
            # First check if we need to delete this cookie.
            # The session should be deleted only if the session is entirely empty
            if settings.SESSION_COOKIE_NAME in request.COOKIES and empty:
                response.delete_cookie(
                    settings.SESSION_COOKIE_NAME,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=host,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )
            else:
                if accessed:
                    patch_vary_headers(response, ('Cookie',))
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    if request.session.get_expire_at_browser_close():
                        max_age = None
                        expires = None
                    else:
                        max_age = request.session.get_expiry_age()
                        expires_time = time.time() + max_age
                        expires = http_date(expires_time)
                    # Save the session data and refresh the client cookie.
                    # Skip session save for 500 responses, refs #3881.
                    if response.status_code != 500:
                        try:
                            request.session.save()
                        except UpdateError:
                            raise SuspiciousOperation(
                                "The request's session was deleted before the "
                                "request completed. The user may have logged "
                                "out in a concurrent request, for example."
                            )
                        response.set_cookie(
                            settings.SESSION_COOKIE_NAME,
                            request.session.session_key, max_age=max_age,
                            expires=expires, domain=host,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                            samesite=settings.SESSION_COOKIE_SAMESITE,
                        )
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
