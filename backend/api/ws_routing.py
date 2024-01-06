from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    path('ws/dev/', consumers.OctoPrintConsumer.as_asgi()),
    path('ws/web/<str:printer_id>/', consumers.WebConsumer.as_asgi()),
    path('ws/janus/<str:printer_id>/', consumers.JanusWebConsumer.as_asgi()),
    path('ws/token/web/<str:token>/', consumers.WebConsumer.as_asgi()),
    path('ws/token/janus/<str:token>/', consumers.JanusWebConsumer.as_asgi()),
    path('ws/share_token/web/<str:share_token>/', consumers.SharedWebConsumer.as_asgi()),
    path('ws/share_token/janus/<str:share_token>/', consumers.JanusSharedWebConsumer.as_asgi()),
    re_path(r'^sockjs/.*$', consumers.OctoprintTunnelWebConsumer.as_asgi()),  # octoprint tunnel
    re_path(r'^websocket$', consumers.OctoprintTunnelWebConsumer.as_asgi())   # mainsail/fluidd tunnel
]
