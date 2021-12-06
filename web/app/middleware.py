from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

from whitenoise.middleware import WhiteNoiseMiddleware

from .views import tunnelv2_views
from lib.tunnelv2 import OctoprintTunnelV2Helper


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


def rename_session_cookie(get_response):

    if settings.SESSION_COOKIE_NAME == 'sessionid':
        raise MiddlewareNotUsed

    def middleware(request):
        if (
            settings.SESSION_COOKIE_NAME != 'sessionid' and
            settings.SESSION_COOKIE_NAME not in request.COOKIES and
            'sessionid' in request.COOKIES
        ):
            request.COOKIES[
                settings.SESSION_COOKIE_NAME
            ] = request.COOKIES['sessionid']

        response = get_response(request)

        if (
            settings.SESSION_COOKIE_NAME != 'sessionid' and
            settings.SESSION_COOKIE_NAME in request.COOKIES and
            'sessionid' in request.COOKIES
        ):
            response.delete_cookie(
                'sessionid',
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
        return response

    return middleware
