from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

import api.ws_routing
from api.authentication import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    # Need to explicity add http as of 3.0
    'http': django_asgi_app,
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            api.ws_routing.websocket_urlpatterns
        )
    ),
})
