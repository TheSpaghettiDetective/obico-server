from channels.routing import ProtocolTypeRouter, URLRouter
from api.authentication import TokenAuthMiddlewareStack
import api.ws_routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            api.ws_routing.websocket_urlpatterns
        )
    ),
})
