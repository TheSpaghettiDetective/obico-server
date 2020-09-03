from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/dev/$', consumers.OctoPrintConsumer),
    url(r'^ws/web/(?P<printer_id>[^/]+)/$', consumers.WebConsumer),
    url(r'^ws/janus/(?P<printer_id>[^/]+)/$', consumers.JanusWebConsumer),
    url(r'^ws/shared/web/(?P<share_token>[^/]+)/$', consumers.WebConsumer),
    url(r'^ws/shared/janus/(?P<share_token>[^/]+)/$', consumers.JanusWebConsumer),
    url(
        r'^octoprint/(?P<printer_id>\d+)/',
        consumers.OctoprintProxyWebConsumer),
]
