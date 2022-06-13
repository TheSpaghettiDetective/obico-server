from typing import List, Dict, Tuple, Optional, Any
import bson
import time
import json
import datetime
import functools

from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
import logging
from sentry_sdk import capture_exception, capture_message
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.forms import model_to_dict
import newrelic.agent
from channels_presence.models import Room
from channels_presence.models import Presence
from django.db.models import F

from lib import cache
from lib import channels
from .octoprint_messages import process_octoprint_status
from app.models import *
from app.models import Print, Printer, ResurrectionError, SharedResource
from lib.tunnelv2 import OctoprintTunnelV2Helper
from lib.view_helpers import touch_user_last_active
from .serializers import *
from .serializers import PublicPrinterSerializer, PrinterSerializer

LOGGER = logging.getLogger(__name__)
TOUCH_MIN_SECS = 30


def close_on_error(msg):
    """
    Method for auth&auth checking.
        - All consumers need to have `connect` method decorated by this method
        - When `connect` method needs to throw an exception when the authenticated subject is not authorized to access the requested resource

    """

    def outer(f):
        @functools.wraps(f)
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception:
                import traceback
                traceback.print_exc()
                LOGGER.exception(msg)
                self.close()
                return
        return inner
    return outer


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

        return Printer.objects.get(
            user=self.scope['user'],
            id=self.scope['url_route']['kwargs']['printer_id']
        )

    @newrelic.agent.background_task()
    @close_on_error('failed to connect')
    def connect(self):
        self.printer = None
        self.printer = self.get_printer()

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            channels.web_group_name(self.printer.id),
            self.channel_name
        )
        self.last_touch = time.time()

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
    def receive_json(self, data, **kwargs):
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        if 'passthru' in data:
            channels.send_msg_to_printer(self.printer.id, data)

    @newrelic.agent.background_task()
    @close_on_error('failed to send')
    def printer_status(self, data):
        serializer = PrinterSerializer(
            Printer.with_archived.get(id=self.printer.id))
        self.send_json(serializer.data)

    @newrelic.agent.background_task()
    def web_message(self, msg):
        self.send_json(msg)


class SharedWebConsumer(WebConsumer):

    def get_printer(self):
        return SharedResource.objects.select_related('printer').get(
            share_token=self.scope['url_route']['kwargs']['share_token']
        ).printer

    @newrelic.agent.background_task()
    def receive_json(self, data, **kwargs):
        # we don't expect frontend sending anything important,
        # this conn is only for status updates from server
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

    @newrelic.agent.background_task()
    @close_on_error('failed to send')
    def printer_status(self, data):
        serializer = PublicPrinterSerializer(
            Printer.with_archived.get(id=self.printer.id)
        )
        self.send_json(serializer.data)

    @newrelic.agent.background_task()
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
    @close_on_error('failed to connect')
    def connect(self):
        self.anomaly_tracker = AnomalyTracker(now())
        self.printer = None

        self.printer = self.get_printer()

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            channels.octo_group_name(self.printer.id),
            self.channel_name
        )

        self.last_touch = time.time()

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
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        try:
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
                printer = Printer.with_archived.annotate(
                    ext_id=F('current_print__ext_id')
                ).get(id=self.printer.id)

                ex: Optional[Exception] = None
                data['_now'] = now()
                try:
                    process_octoprint_status(printer, data)
                    self.anomaly_tracker.track(printer, data)
                except ResurrectionError as ex:
                    self.anomaly_tracker.track(printer, data, ex)

        except ObjectDoesNotExist:
            import traceback
            traceback.print_exc()
            self.close()
        except Exception:  # sentry doesn't automatically capture consumer errors
            import traceback
            traceback.print_exc()
            capture_exception()

    @newrelic.agent.background_task()
    def printer_message(self, data):
        try:
            as_binary = data.get('as_binary', False)
            if as_binary:
                self.send(text_data=None, bytes_data=bson.dumps(data))
            else:
                self.send(text_data=json.dumps(data))
        except Exception:  # sentry doesn't automatically capture consumer errors
            LOGGER.error(data)
            import traceback
            traceback.print_exc()
            capture_exception()


class JanusWebConsumer(WebsocketConsumer):

    def get_printer(self):
        if 'token' in self.scope['url_route']['kwargs']:
            return Printer.objects.get(
                auth_token=self.scope['url_route']['kwargs']['token'],
            )

        return Printer.objects.get(
            user=self.scope['user'],
            id=self.scope['url_route']['kwargs']['printer_id']
        )

    @newrelic.agent.background_task()
    @close_on_error('failed to connect')
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
    def receive(self, text_data=None, bytes_data=None):
        channels.send_msg_to_printer(self.printer.id, {'janus': text_data})

    @newrelic.agent.background_task()
    def janus_message(self, msg):
        self.send(text_data=msg.get('msg'))


class JanusSharedWebConsumer(JanusWebConsumer):

    def get_printer(self):
        return SharedResource.objects.select_related('printer').get(
            share_token=self.scope['url_route']['kwargs']['share_token']
        ).printer

    @newrelic.agent.background_task()
    def receive(self, text_data=None, bytes_data=None):
        # we are going to disable datachannel for shared printer connections
        # by tampering janus offer/answer messages

        msg = json.loads(text_data)
        if 'jsep' in msg and msg['jsep']['type'] == 'answer':
            sdp = msg['jsep']['sdp']

            if 'BUNDLE video\r\n' not in sdp:
                # frontend should request only video,
                # if thats's not the case, then something went wrong
                # with patching the offer (bellow)
                capture_message(
                    'bad sdp bundle',
                    extras={'sdp': sdp}
                )
                return

        channels.send_msg_to_printer(self.printer.id, {'janus': text_data})

    @newrelic.agent.background_task()
    def janus_message(self, message):
        # we are going to disable datachannel for shared printer connections
        # by tampering janus offer/answer messages

        msg = json.loads(message['msg'])
        if 'jsep' in msg and msg['jsep']['type'] == 'offer':
            sdp = msg['jsep']['sdp']

            if 'BUNDLE video data\r\n' not in sdp:
                # only valid case here is when video is disabled in the plugin,
                # "BUNDLE data"
                # ... in that case no need to continue negotiation, as plugin
                # has nothing to offer.

                # all other cases are unexpected,
                # no need to let them go through.
                return

            # removing data from bundle
            sdp = sdp.replace('BUNDLE video data', 'BUNDLE video')

            # datachannel related parts are at the end of sdp,
            # this is the starting position
            delete_from = sdp.find('m=application')

            if delete_from < 0:
                # too strange, ignoring message
                capture_message(
                    'missing application from sdp bundle',
                    extras={'sdp': sdp}
                )
                return

            sdp = sdp[:delete_from]

            msg['jsep']['sdp'] = sdp

        self.send(text_data=json.dumps(msg))


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
    def connect(self):
        self.user, self.printer = None, None
        try:
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
        except Exception:
            LOGGER.exception("Websocket failed to connect")
            self.close()

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
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if self.printer.user.tunnel_usage_over_cap():
            return

        try:
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
        except Exception:  # sentry doesn't automatically capture consumer errors
            import traceback
            traceback.print_exc()
            capture_exception()

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

            cache.octoprinttunnel_update_stats(self.printer.user_id, len(payload['data']))
        except Exception:  # sentry doesn't automatically capture consumer errors
            import traceback
            traceback.print_exc()
            capture_exception()


class AnomalyTracker:

    def __init__(self, connected_at: datetime) -> None:
        self.connected_at = connected_at
        self.transition_history: List[Tuple[int, Dict]] = []
        self.last_ext_id: Optional[int] = None
        self.last_failed = False

    def track(self, printer: Printer, status: Dict[str, Any], ex: Optional[Exception] = None) -> None:
        if len(self.transition_history) > 0:
            idx = self.transition_history[-1][0] + 1
        else:
            idx = 0

        comeback = False
        ext_id = status.get('current_print_ts', None)
        if self.last_ext_id != ext_id:
            self.last_failed = False
            self.transition_history.append((idx, status))
            if ext_id != -1:
                comeback = [
                    _st.get('current_print_ts', None)
                    for (_, _st) in self.transition_history
                ].count(ext_id) > 1

            if len(self.transition_history) > 10:
                self.transition_history[-10:]

        self.last_ext_id = ext_id

        if (comeback or ex) and not self.last_failed:
            self.report_resurrection(
                comeback=comeback,
                ex=ex is not None,
                printer=printer,
                transition_history=self.transition_history,
            )

        self.last_failed = comeback or (ex is not None)

    def report_resurrection(self, comeback: bool, ex: bool, printer: 'Printer', transition_history: List[Tuple[int, Dict]]) -> None:
        data: Dict[str, Any] = {
            'connected_at': self.connected_at,
            'comeback': comeback,
            'ex': ex,
        }

        seen = set()
        for (i, status) in transition_history:
            data[f'status{str(i).zfill(4)}'] = status
            ext_id = status.get('current_print_ts', None)
            if ext_id not in seen:
                print = Print.all_objects.filter(
                    printer=printer,
                    ext_id=ext_id
                ).first()
                if print:
                    data[f'print.{ext_id}'] = model_to_dict(print)
                    data[f'print.{ext_id}']['deleted'] = print.deleted
                seen.add(ext_id)

        data['printer.ext_id'] = printer.ext_id
        data['print.current'] = model_to_dict(
            printer.current_print) if printer.current_print else None

        capture_message(
            'Resurrected print',
            extras=data,
        )
