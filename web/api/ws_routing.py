from django.conf.urls import url, re_path

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/dev/$', consumers.OctoPrintConsumer),
    url(r'^ws/web/(?P<printer_id>[^/]+)/$', consumers.WebConsumer),
    url(r'^ws/janus/(?P<printer_id>[^/]+)/$', consumers.JanusWebConsumer),
    url(r'^ws/token/web/(?P<token>[^/]+)/$', consumers.WebConsumer),
    url(r'^ws/token/janus/(?P<token>[^/]+)/$', consumers.JanusWebConsumer),
    url(r'^ws/share_token/web/(?P<share_token>[^/]+)/$',
        consumers.SharedWebConsumer),
    url(r'^ws/share_token/janus/(?P<share_token>[^/]+)/$',
        consumers.JanusSharedWebConsumer),
    re_path(r'^sockjs/.*$', consumers.OctoprintTunnelWebConsumer)
]
