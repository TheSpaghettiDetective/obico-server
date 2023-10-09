from django.urls import path
from django.conf.urls import re_path

from . import consumers

websocket_urlpatterns = [
    path('ws/dev/', consumers.OctoPrintConsumer),
    path('ws/web/<str:printer_id>/', consumers.WebConsumer),
    path('ws/janus/<str:printer_id>/', consumers.JanusWebConsumer),
    path('ws/token/web/<str:token>/', consumers.WebConsumer),
    path('ws/token/janus/<str:token>/', consumers.JanusWebConsumer),
    path('ws/share_token/web/<str:share_token>/',
        consumers.SharedWebConsumer),
    path('ws/share_token/janus/<str:share_token>/',
        consumers.JanusSharedWebConsumer),
    re_path(r'^sockjs/.*$', consumers.OctoprintTunnelWebConsumer), # octoprint tunnel
    re_path(r'^websocket$', consumers.OctoprintTunnelWebConsumer)  # mainsail/fluidd tunnel
]
