from django.conf import settings
from .views import tunnelv2_views

from whitenoise.middleware import WhiteNoiseMiddleware


class TSDWhiteNoiseMiddleware(WhiteNoiseMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        path = settings.WELL_KNOWN_PATH
        if path:
            self.add_files(path, prefix="/.well-known")

    def process_request(self, request):
        m = settings.OCTOPRINT_TUNNEL_HOST_RE.match(request.get_host())

        if m is not None:
            return

        return super().process_request(request)


def octoprint_tunnelv2(get_response):

    def middleware(request):
        m = settings.OCTOPRINT_TUNNEL_HOST_RE.match(request.get_host())
        if m is not None:
            pk = int(m.groups()[0])
            return tunnelv2_views.octoprint_http_tunnel(request, pk)

        response = get_response(request)
        return response

    return middleware
