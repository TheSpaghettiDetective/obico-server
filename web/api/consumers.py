from typing import List, Dict, Tuple
import bson
import json

from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
import logging
from raven.contrib.django.raven_compat.models import client as sentryClient
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
import newrelic.agent
from channels_presence.models import Room
from channels_presence.models import Presence


from lib import cache
from lib import channels
from .octoprint_messages import process_octoprint_status
from app.models import *
from app.models import Print, Printer, ResurrectionError, PrintEvent
from django.forms import model_to_dict

from .serializers import *


LOGGER = logging.getLogger(__name__)


class WebConsumer(JsonWebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        try:
            if self.scope['path'].startswith('/ws/share_token/') or self.scope['path'].startswith('/ws/token/'):
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

    @newrelic.agent.background_task()
    def receive_json(self, data, **kwargs):
        Presence.objects.touch(self.channel_name)
        if 'passthru' in data:
            channels.send_msg_to_printer(self.printer.id, data)

    @newrelic.agent.background_task()
    def printer_status(self, data):
        try:
            serializer = PrinterSerializer(Printer.with_archived.get(id=self.printer.id))
            self.send_json(serializer.data)
        except:
            sentryClient.captureException()

    @newrelic.agent.background_task()
    def web_message(self, msg):
        self.send_json(msg)

    def current_user(self):
        return self.scope['user']


class OctoPrintConsumer(WebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        self.status_history: List[Tuple[int, Dict]] = []

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

        # disconnect all octoprint tunnels
        channels.send_message_to_octoprinttunnel(
            channels.octoprinttunnel_group_name(self.current_printer().id),
            {'type': 'octoprint_close', 'ref': 'ALL'},
        )

    @newrelic.agent.background_task()
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
                cache.octoprinttunnel_http_response_set(
                    data['http.tunnel']['ref'],
                    data['http.tunnel']
                )
            elif 'ws.tunnel' in data:
                channels.send_message_to_octoprinttunnel(
                    channels.octoprinttunnel_group_name(self.current_printer().id),
                    data['ws.tunnel'],
                )
            elif 'passthru' in data:
                channels.send_message_to_web(printer.id, data)
            else:
                idx = self.status_history[-1][0] + 1 if len(self.status_history) else 0
                self.status_history.append((idx, data))
                if len(self.status_history) > 15:
                    self.status_history = self.status_history[-15:]
                try:
                    process_octoprint_status(printer, data)
                except ResurrectionError as ex:
                    report_resurrection(printer, ex.print, self.status_history)

        except ObjectDoesNotExist:
            import traceback; traceback.print_exc()
            self.close()
        except:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            sentryClient.captureException()

    @newrelic.agent.background_task()
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
            if self.scope['path'].startswith('/ws/share_token/') or self.scope['path'].startswith('/ws/token/'):
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

    @newrelic.agent.background_task()
    def janus_message(self, msg):
        self.send(text_data=msg.get('msg'))


class OctoprintTunnelWebConsumer(WebsocketConsumer):

    # default 1000 does not trigger retries in octoprint webapp
    OCTO_WS_ERROR_CODE = 3000

    @newrelic.agent.background_task()
    def connect(self):
        try:
            # Exception for un-authenticated or un-authorized access
            self.printer = Printer.objects.select_related('user').get(
                user=self.current_user(),
                id=self.scope['url_route']['kwargs']['printer_id'])
            self.path = self.scope['path'][len(f'/ws/octoprint/{self.printer.id}'):]  # FIXME
            self.ref = self.scope['path']
            self.group_name = channels.octoprinttunnel_group_name(
                self.printer.id)

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
                        'ref': self.ref,
                        'data': None,
                        'path': self.path,
                        'type': 'connect',
                    },
                    'as_binary': True,
                })
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn(f'OctoprintTunnelWebConsumer: Closed websocket with code: {close_code}')
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name)
        Room.objects.remove(
            self.group_name,
            self.channel_name)

        channels.send_msg_to_printer(
            self.printer.id,
            {
                'ws.tunnel': {
                    'ref': self.ref,
                    'data': None,
                    'path': self.path,
                    'type': 'tunnel_close',
                },
                'as_binary': True,
            })

    @newrelic.agent.background_task()
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if self.printer.user.tunnel_usage_over_cap():
            return

        try:
            Presence.objects.touch(self.channel_name)
            channels.send_msg_to_printer(
                self.printer.id,
                {
                    'ws.tunnel': {
                        'ref': self.ref,
                        'data': text_data or bytes_data,
                        'path': self.path,
                        'type': 'tunnel_message',
                    },
                    'as_binary': True
                })
        except:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            sentryClient.captureException()

    @newrelic.agent.background_task()
    def octoprinttunnel_message(self, msg, **kwargs):
        try:
            # msg == {'data': {'type': ..., 'data': ..., 'ref': ...}, ...}
            payload = msg['data']

            if payload['ref'] != self.ref and payload['ref'] != 'ALL':
                return

            if payload['type'] == 'octoprint_close':
                self.close(self.OCTO_WS_ERROR_CODE)
                return

            if isinstance(payload['data'], bytes):
                self.send(bytes_data=payload['data'])
            else:
                self.send(text_data=payload['data'])

            cache.octoprinttunnel_update_stats(
                self.scope['user'].id,
                len(payload['data']) * 1.2 * 2  # x1.2 because sent data volume is 20% of received. x2 because all data need to go in and out
            )
        except:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            sentryClient.captureException()

    def current_user(self):
        return self.scope['user']


def report_resurrection(printer: 'Printer', cur_print: 'Print', status_history: List[Tuple[int, Dict]]):
    data = {}
    for (i, status) in status_history:
        data[f'status{str(i).zfill(4)}'] = status

    data['print'] = model_to_dict(cur_print)  # noqa: F841
    data['print']['deleted'] = cur_print.deleted
    if printer.current_print:
        data['current_print'] = model_to_dict(  # noqa: F841
            printer.current_print)

    evqs = PrintEvent.objects.filter(
        print__printer=printer
    ).order_by(
        '-created_at'
    ).values(
        'print__ext_id', 'event_type', 'created_at'
    )[:10]

    for i, ev in enumerate(evqs):
        data[f'event{str(i).zfill(2)}'] = dict(**ev)

    from raven import Client
    c = Client()
    c.extra_context(data=data)
    c.captureMessage('Dead print alive')
