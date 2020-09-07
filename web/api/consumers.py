import bson
import json
import hashlib

from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import logging
from raven.contrib.django.raven_compat.models import client as sentryClient
from django.core.exceptions import ObjectDoesNotExist
import newrelic.agent
from channels_presence.models import Room
from channels_presence.models import Presence

from lib import redis
from lib import channels
from .octoprint_messages import process_octoprint_status
from app.models import *
from .serializers import *

LOGGER = logging.getLogger(__name__)


class WebConsumer(JsonWebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        try:
            if self.scope['path'].startswith('/ws/shared/'):
                self.printer = self.current_user()
            else:
                # Exception for un-authenticated or un-authorized access
                self.printer = Printer.objects.get(user=self.current_user(), id=self.scope['url_route']['kwargs']['printer_id'])

            async_to_sync(self.channel_layer.group_add)(
                channels.web_group_name(self.printer.id),
                self.channel_name
            )
            self.accept()
            Room.objects.add(channels.web_group_name(self.printer.id), self.channel_name)
            self.printer_status(None)   # Send printer status to web frontend as soon as it connects
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("WebConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.web_group_name(self.printer.id),
            self.channel_name
        )
        Room.objects.remove(channels.web_group_name(self.printer.id), self.channel_name)

    def receive_json(self, data, **kwargs):
        Presence.objects.touch(self.channel_name)
        if 'passthru' in data:
            channels.send_msg_to_printer(self.printer.id, data)

    def printer_status(self, data):
        try:
            serializer = PrinterSerializer(Printer.with_archived.get(id=self.printer.id))
            self.send_json(serializer.data)
        except:
            sentryClient.captureException()

    def web_message(self, msg):
        self.send_json(msg)

    def current_user(self):
        return self.scope['user']


class OctoPrintConsumer(WebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        if self.current_printer().is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                channels.octo_group_name(self.current_printer().id),
                self.channel_name
            )
            self.accept()
            Room.objects.add(channels.octo_group_name(self.current_printer().id), self.channel_name)
            # Send remote status to OctoPrint as soon as it connects
            self.current_printer().send_should_watch_status()
            channels.send_viewing_status(self.current_printer().id)
        else:
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("OctoPrintConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.octo_group_name(self.current_printer().id),
            self.channel_name
        )
        Room.objects.remove(channels.octo_group_name(self.current_printer().id), self.channel_name)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        Presence.objects.touch(self.channel_name)
        try:
            printer = Printer.with_archived.get(id=self.current_printer().id)

            if text_data:
                data = json.loads(text_data)
            else:
                data = bson.loads(bytes_data)

            if 'janus' in data:
                channels.send_janus_to_web(self.current_printer().id, data.get('janus'))
            elif 'http.tunnel' in data:
                redis.octoprinttunnel_http_response_set(
                    data['http.tunnel']['ref'],
                    data['http.tunnel']
                )
            elif 'ws.tunnel' in data:
                channels.send_message_to_octoprinttunnel(
                    data['ws.tunnel']['ref'],
                    data['ws.tunnel']['data']
                )
            elif 'passthru' in data:
                channels.send_message_to_web(printer.id, data)
            else:
                process_octoprint_status(printer, data)

        except ObjectDoesNotExist:
            import traceback; traceback.print_exc()
            self.close()
        except:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            self.close()
            sentryClient.captureException()

    def printer_message(self, data):
        try:
            as_binary = data.get('as_binary', False)
            if as_binary:
                self.send(text_data=None, bytes_data=bson.dumps(data))
            else:
                self.send(text_data=json.dumps(data))
        except:  # sentry doesn't automatically capture consumer errors
            LOGGER.error(data)
            import traceback; traceback.print_exc()
            sentryClient.captureException()

    def current_printer(self):
        return self.scope['user']


class JanusWebConsumer(WebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        try:
            if self.scope['path'].startswith('/ws/shared/'):
                self.printer = self.scope['user']
            else:
                # Exception for un-authenticated or un-authorized access
                self.printer = Printer.objects.get(user=self.scope['user'], id=self.scope['url_route']['kwargs']['printer_id'])

            async_to_sync(self.channel_layer.group_add)(
                channels.janus_web_group_name(self.printer.id),
                self.channel_name
            )
            self.accept('janus-protocol')
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("WebConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.janus_web_group_name(self.printer.id),
            self.channel_name
        )

    @newrelic.agent.background_task()
    def receive(self, text_data=None, bytes_data=None):
        channels.send_msg_to_printer(self.printer.id, {'janus': text_data})

    def janus_message(self, msg):
        self.send(text_data=msg.get('msg'))


class OctoprintTunnelWebConsumer(WebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        try:
            # Exception for un-authenticated or un-authorized access
            self.printer = Printer.objects.get(
                user=self.current_user(),
                id=self.scope['url_route']['kwargs']['printer_id'])
            self.path = self.scope['path'][len(f'/ws/octoprint/{self.printer.id}'):]  # FIXME
            self.group_name = channels.octoprinttunnel_group_name(
                self.printer.id,
                hashlib.md5(self.path.encode()).hexdigest())

            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()
            Room.objects.add(
                self.group_name,
                self.channel_name)

            channels.send_msg_to_printer(
                self.printer.id,
                {
                    'ws.tunnel': {
                        'ref': self.group_name,
                        'data': None,
                        'path': self.path,
                    },
                    'as_binary': True,
                })
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn(
            "OctoprintTunnelWebConsumer: Closed websocket with code: "
            "{}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name)
        Room.objects.remove(
            self.group_name,
            self.channel_name)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        Presence.objects.touch(self.channel_name)
        channels.send_msg_to_printer(
            self.printer.id,
            {
                'ws.tunnel': {
                    'ref': self.group_name,
                    'data': text_data or bytes_data,
                    'path': self.path,
                },
                'as_binary': True
            })

    def octoprinttunnel_message(self, msg, **kwargs):
        if isinstance(msg['data'], bytes):
            self.send(bytes_data=msg['data'])
        else:
            self.send(text_data=msg['data'])

    def current_user(self):
        return self.scope['user']
