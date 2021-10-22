from django.conf import settings

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
