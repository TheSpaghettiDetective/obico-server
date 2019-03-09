# chat/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/dev/$', consumers.OctoPrintConsumer),
    url(r'^ws/web/(?P<printer_id>[^/]+)/$', consumers.WebConsumer),
]
