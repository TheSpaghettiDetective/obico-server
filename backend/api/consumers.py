import bson
import time
import json
import functools
from typing import Callable, Optional, Union, Tuple

from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
import logging
from sentry_sdk import capture_exception, capture_message, isolation_scope
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
import newrelic.agent
from channels_presence.models import Room
from channels_presence.models import Presence

from lib import cache
from lib import channels
from .octoprint_messages import process_printer_status
from app.models import *
from lib.tunnelv2 import OctoprintTunnelV2Helper, TunnelAuthenticationError
from lib.view_helpers import touch_user_last_active
from .serializers import *
from .serializers import PublicPrinterSerializer, PrinterSerializer

LOGGER = logging.getLogger(__name__)
TOUCH_MIN_SECS = 30
STATUS_UPDATE_MIN_SECS = 45


def report_error(
    fn: Optional[Callable] = None,
    *,
    exc_class: Optional[Union[Exception, Tuple[Exception, ...]]] = None,
    msg: str = '',
    sentry: bool = True,
    close: bool = False,
) -> Callable:
    """Decorator for consumer message handlers. May close connections on error and reports causes to sentry."""

    # @decorator vs @partial_decorator
    # When decorator is a partial function, we need to handle it differently, as fn comes as an argument.
    if fn is not None:
        return report_error(None, exc_class=exc_class, msg=msg, sentry=sentry, close=close)(fn)

    klass = Exception if exc_class is None else exc_class
    def outer(fn):
        @functools.wraps(fn)
        def inner(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except klass as exc:
                import traceback
                traceback.print_exc()
                LOGGER.exception(msg or f'{exc.__class__.__name__} in {fn.__module__}.{fn.__qualname__}')
                if sentry:
                    # Get user info if available
                    user_info = None
                    if hasattr(self, 'scope') and 'user' in self.scope and self.scope['user'].is_authenticated:
                        user_info = {'id': self.scope['user'].id}
                    elif hasattr(self, 'user') and self.user and self.user.is_authenticated:
                        user_info = {'id': self.user.id}
                    elif hasattr(self, 'get_printer') and self.get_printer():
                        user_info = {'id': self.get_printer().user.id}

                    if user_info:
                        with isolation_scope() as scope:
                            scope.set_user(user_info)
                            capture_exception()
                    else:
                        capture_exception()

                if close:
                    self.close()
                return
        return inner
    return outer


close_on_error = functools.partial(report_error, close=True)
close_on_error.__doc__ = """Reports error and closes consumer connection when specified exception raised"""


class WebConsumer(JsonWebsocketConsumer):

    def get_printer(self):
        """
        2 ways to authenticate:
            1. `printer.auth_token` as part of the request parameters.
            2. Django session cookie so that `self.scope['user']` is set
        """

        if 'token' in self.scope['url_route']['kwargs']:
            return Printer.objects.get(
                auth_token=self.scope['url_route']['kwargs']['token'],
            )

        if not self.scope['user'].is_authenticated:
            raise Printer.DoesNotExist('session is not authenticated')

        return Printer.objects.get(
            user=self.scope['user'],
            id=self.scope['url_route']['kwargs']['printer_id']
        )

    @newrelic.agent.background_task()
    @close_on_error
    @close_on_error(exc_class=Printer.DoesNotExist, sentry=False) # Printer.DoesNotExist means auth failure and hence is expected
    def connect(self):
        self.printer = None
        self.printer = self.get_printer()

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            channels.web_group_name(self.printer.id),
            self.channel_name
        )
        self.last_touch = time.time()
        self.printer_status_last_sent = 0

        Room.objects.add(
            channels.web_group_name(self.printer.id),
            self.channel_name
        )

        # Send printer status to web frontend as soon as it connects
        self.printer_status(None)

        touch_user_last_active(self.printer.user)

    def disconnect(self, close_code):
        LOGGER.warn(
            "WebConsumer: Closed websocket with code: {}".format(close_code))
        if self.printer:
            async_to_sync(self.channel_layer.group_discard)(
                channels.web_group_name(self.printer.id),
                self.channel_name
            )
            Room.objects.remove(
                channels.web_group_name(self.printer.id),
                self.channel_name
            )

    @newrelic.agent.background_task()
    @report_error
    def receive_json(self, data, **kwargs):
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        if not data and time.time() - self.printer_status_last_sent > STATUS_UPDATE_MIN_SECS:
            # Empty message from client is a signal for getting status to trigger a re-render in the client
            channels.send_status_to_web(self.printer.id)

        if 'passthru' in data:
            channels.send_msg_to_printer(self.printer.id, data)

    @newrelic.agent.background_task()
    @close_on_error
    def printer_status(self, data):
        serializer = PrinterSerializer(
            Printer.with_archived.get(id=self.printer.id))
        self.send_json(serializer.data)
        self.printer_status_last_sent = time.time()

    @newrelic.agent.background_task()
    @report_error
    def web_message(self, msg):
        self.send_json(msg)


class SharedWebConsumer(WebConsumer):

    def get_printer(self):
        return SharedResource.objects.select_related('printer').get(
            share_token=self.scope['url_route']['kwargs']['share_token']
        ).printer

    @newrelic.agent.background_task()
    @report_error
    def receive_json(self, data, **kwargs):
        # we don't expect frontend sending anything important,
        # this conn is only for status updates from server
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

    @newrelic.agent.background_task()
    @close_on_error
    def printer_status(self, data):
        serializer = PublicPrinterSerializer(
            Printer.with_archived.get(id=self.printer.id)
        )
        self.send_json(serializer.data)

    @newrelic.agent.background_task()
    @report_error
    def web_message(self, msg):
        # frontend (should be) interested only in printer_status messages
        pass


class OctoPrintConsumer(WebsocketConsumer):

    def get_printer(self):
        headers = dict(self.scope['headers'])
        if b'authorization' in headers:
            for v in headers[b'authorization'].split(b','):
                token_name, token_key = v.decode().split()
                if token_name == 'bearer':
                    return Printer.objects.select_related('user').get(
                        auth_token=token_key
                    )

        raise Exception('missing auth header')

    @newrelic.agent.background_task()
    @close_on_error
    @close_on_error(exc_class=Printer.DoesNotExist, sentry=False) # Printer.DoesNotExist means auth failure and hence is expected
    def connect(self):
        self.connected_at = time.time()
        self.printer = None

        self.printer = self.get_printer()

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            channels.octo_group_name(self.printer.id),
            self.channel_name
        )

        self.last_touch = self.connected_at

        Room.objects.add(
            channels.octo_group_name(self.printer.id),
            self.channel_name
        )

        # Send remote status to OctoPrint as soon as it connects
        self.printer_message({'remote_status': {
            'viewing': channels.num_ws_connections(
                channels.web_group_name(self.printer.id)) > 0,
            'should_watch': self.printer.should_watch(),
        }})

        async_to_sync(self.channel_layer.group_send)(
            channels.octo_group_name(self.printer.id),
            {
                'type': 'close.duplicates',
                'channel_name': self.channel_name,
                'connected_at': self.connected_at
            }
        )

        touch_user_last_active(self.printer.user)

    def disconnect(self, close_code):
        LOGGER.warn(
            "OctoPrintConsumer: Closed websocket with code: {}".format(close_code))
        if self.printer:
            async_to_sync(self.channel_layer.group_discard)(
                channels.octo_group_name(self.printer.id),
                self.channel_name
            )

            Room.objects.remove(
                channels.octo_group_name(self.printer.id),
                self.channel_name
            )

            # disconnect all octoprint tunnels
            channels.send_message_to_octoprinttunnel(
                channels.octoprinttunnel_group_name(self.printer.id),
                {'type': 'octoprint_close', 'ref': 'ALL'},
            )

    @newrelic.agent.background_task()
    @report_error
    @close_on_error(exc_class=Printer.DoesNotExist, sentry=False) # Printer.DoesNotExist means auth failure and hence is expected
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        if text_data:
            data = json.loads(text_data)
        else:
            data = bson.loads(bytes_data)

        if 'janus' in data:
            channels.send_janus_to_web(
                self.printer.id, data.get('janus'))
        elif 'http.tunnelv2' in data:
            cache.octoprinttunnel_http_response_set(
                data['http.tunnelv2']['ref'],
                data['http.tunnelv2']
            )
        elif 'ws.tunnel' in data:
            channels.send_message_to_octoprinttunnel(
                channels.octoprinttunnel_group_name(self.printer.id),
                data['ws.tunnel'],
            )
        elif 'passthru' in data:
            channels.send_message_to_web(self.printer.id, data)
        else:
            self.printer.refresh_from_db()
            if self.printer.deleted:
                # Printer deleted. Close the connection.
                self.close()
                return

            process_printer_status(self.printer, data)

    @newrelic.agent.background_task()
    @report_error
    def printer_message(self, data):
        as_binary = data.get('as_binary', False)
        if as_binary:
            self.send(text_data=None, bytes_data=bson.dumps(data))
        else:
            self.send(text_data=json.dumps(data))

    @newrelic.agent.background_task()
    @report_error
    def close_duplicates(self, data):
        channel_name = data['channel_name']
        connected_at = data['connected_at']
        if self.channel_name != channel_name and self.connected_at <= connected_at:
            LOGGER.warning(f'closing possibly duplicate connection from printer pk:{self.printer.id}')
            self.close(code=4321)


class JanusWebConsumer(WebsocketConsumer):
    def get_printer(self):
        if 'token' in self.scope['url_route']['kwargs']:
            return Printer.objects.get(
                auth_token=self.scope['url_route']['kwargs']['token'],
            )

        # Mobileraker wants to use tunnel credential to connect janus websocket
        try:
            pt = OctoprintTunnelV2Helper.get_octoprinttunnel(self.scope)
            if pt and str(pt.printer_id) == self.scope['url_route']['kwargs']['printer_id']:
                return pt.printer
        except TunnelAuthenticationError:
            pass    # Continue to other ways of authentication

        if not self.scope['user'].is_authenticated:
            raise Printer.DoesNotExist('session is not authenticated')

        return Printer.objects.get(
            user=self.scope['user'],
            id=self.scope['url_route']['kwargs']['printer_id']
        )

    @newrelic.agent.background_task()
    @close_on_error
    @close_on_error(exc_class=Printer.DoesNotExist, sentry=False) # Printer.DoesNotExist means auth failure and hence is expected
    def connect(self):
        self.printer = None
        self.printer = self.get_printer()

        async_to_sync(self.channel_layer.group_add)(
            channels.janus_web_group_name(self.printer.id),
            self.channel_name
        )

        self.accept('janus-protocol')

    def disconnect(self, close_code):
        LOGGER.warn("JanusWebConsumer: Closed with code: {}".format(close_code))
        if self.printer:
            async_to_sync(self.channel_layer.group_discard)(
                channels.janus_web_group_name(self.printer.id),
                self.channel_name
            )

    @newrelic.agent.background_task()
    @report_error
    def receive(self, text_data=None, bytes_data=None):
        channels.send_msg_to_printer(self.printer.id, {'janus': text_data})

    @newrelic.agent.background_task()
    @report_error
    def janus_message(self, msg):
        self.send(text_data=msg.get('msg'))


class JanusSharedWebConsumer(JanusWebConsumer):

    def get_printer(self):
        return SharedResource.objects.select_related('printer').get(
            share_token=self.scope['url_route']['kwargs']['share_token']
        ).printer


class OctoprintTunnelWebConsumer(WebsocketConsumer):

    # default 1000 does not trigger retries in octoprint webapp
    OCTO_WS_ERROR_CODE = 3000

    def get_user_and_printer(self):
        pt = OctoprintTunnelV2Helper.get_octoprinttunnel(self.scope)
        if pt:
            return (
                pt.printer.user,
                pt.printer
            )
        return (None, None)

    @newrelic.agent.background_task()
    @close_on_error
    @close_on_error(exc_class=(Printer.DoesNotExist, TunnelAuthenticationError), sentry=False) # TunnelAuthenticationError: auth error, Printer.DoesNotExist: missing printer/not authorized
    def connect(self):
        self.user, self.printer = None, None
        # Exception for un-authenticated or un-authorized access
        self.user, self.printer = self.get_user_and_printer()
        if self.printer is None:
            self.close()
            return

        self.accept()

        self.path = self.scope['path']

        self.ref = str(time.time())

        async_to_sync(self.channel_layer.group_add)(
            channels.octoprinttunnel_group_name(self.printer.id),
            self.channel_name,
        )
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

    def disconnect(self, close_code):
        LOGGER.warn(
            f'OctoprintTunnelWebConsumer: Closed websocket with code: {close_code}')

        if not self.printer:
            return

        async_to_sync(self.channel_layer.group_discard)(
            channels.octoprinttunnel_group_name(self.printer.id),
            self.channel_name,
        )

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
    @report_error
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if self.printer.user.tunnel_usage_over_cap():
            return

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

    @newrelic.agent.background_task()
    @report_error
    def octoprinttunnel_message(self, msg, **kwargs):
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

        cache.octoprinttunnel_update_stats(self.printer.user_id, len(payload['data']))
