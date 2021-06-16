from typing import List, Dict, Tuple, Optional, Any
import bson
import time
import json
import datetime
import functools
import urllib.parse

from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
import logging
from raven.contrib.django.raven_compat.models import client as sentryClient
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.forms import model_to_dict
import newrelic.agent
from channels_presence.models import Room
from channels_presence.models import Presence
from django.db.models import F


from lib import cache
from lib import channels
from lib.utils import str_to_hash
from .octoprint_messages import process_octoprint_status
from app.models import *
from app.models import Print, Printer, ResurrectionError
from .serializers import *
from .serializers import LinkHelperQueryResponseSerializer

LOGGER = logging.getLogger(__name__)
TOUCH_MIN_SECS = 30


class WebConsumer(JsonWebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        try:
            if self.scope['path'].startswith('/ws/share_token/') or self.scope['path'].startswith('/ws/token/'):
                self.printer = self.current_user()
            else:
                # Throw exception in case of un-authenticated or un-authorized access
                self.printer = Printer.objects.get(user=self.current_user(), id=self.scope['url_route']['kwargs']['printer_id'])

            self.accept()

            async_to_sync(self.channel_layer.group_add)(
                channels.web_group_name(self.printer.id),
                self.channel_name
            )
            self.last_touch = time.time()
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
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        if 'passthru' in data:
            channels.send_msg_to_printer(self.printer.id, data)

    @newrelic.agent.background_task()
    def printer_status(self, data):
        try:
            if self.scope['path'].startswith('/ws/share_token/'):
                serializer = PublicPrinterSerializer(Printer.with_archived.get(id=self.printer.id))
            else:
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
        self.anomaly_tracker = AnomalyTracker(now())

        if self.current_printer().is_authenticated:
            self.accept()
            async_to_sync(self.channel_layer.group_add)(
                channels.octo_group_name(self.current_printer().id),
                self.channel_name
            )
            self.last_touch = time.time()
            Room.objects.add(channels.octo_group_name(self.current_printer().id), self.channel_name)
            # Send remote status to OctoPrint as soon as it connects
            self.printer_message({'remote_status': {
                'viewing': channels.num_ws_connections(channels.web_group_name(self.current_printer().id)) > 0,
                'should_watch': self.current_printer().should_watch(),
            }})
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
        if time.time() - self.last_touch > TOUCH_MIN_SECS:
            self.last_touch = time.time()
            Presence.objects.touch(self.channel_name)

        try:
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
                channels.send_message_to_web(self.current_printer().id, data)
            else:
                printer = Printer.with_archived.annotate(
                    ext_id=F('current_print__ext_id')
                ).get(id=self.current_printer().id)

                ex: Optional[Exception] = None
                data['_now'] = now()
                try:
                    process_octoprint_status(printer, data)
                    self.anomaly_tracker.track(printer, data)
                except ResurrectionError as ex:
                    self.anomaly_tracker.track(printer, data, ex)

        except ObjectDoesNotExist:
            import traceback; traceback.print_exc()
            self.close()
        except Exception:  # sentry doesn't automatically capture consumer errors
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
        LOGGER.warn("JanusWebConsumer: Closed websocket with code: {}".format(close_code))
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
            self.accept()

            self.path = self.scope['path'][len(f'/ws/octoprint/{self.printer.id}'):]  # FIXME
            self.ref = self.scope['path']

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
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn(f'OctoprintTunnelWebConsumer: Closed websocket with code: {close_code}')
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


def catch_all(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            sentryClient.captureException()
    return wrapper


def catch_all_and_close(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            sentryClient.captureException()
            self.close()
    return wrapper


class LinkHelperConsumer(WebsocketConsumer):

    @catch_all_and_close
    def connect(self):
        ip = self.get_client_ip()
        self.ip_hash = str_to_hash(ip)

        device_id = urllib.parse.parse_qs(
            self.scope['query_string']
        )[b'device_id'][0].decode()

        if not device_id.isalnum() or len(device_id) != 32:
            raise Exception('LinkHelperConsumer: unexpected device_id')
        self.device_id = device_id

        self.accept()
        LOGGER.debug(f"LinkHelperConsumer: detected ip: {ip} ip_hash: {self.ip_hash} device_id: {self.device_id}")

        async_to_sync(self.channel_layer.group_add)(
            channels.linkhelper_group_name(self.ip_hash),
            self.channel_name,
        )

    def disconnect(self, close_code):
        LOGGER.warn("LinkHelperConsumer: Closed websocket with code: {}".format(close_code))
        if hasattr(self, 'ip_hash'):
            async_to_sync(self.channel_layer.group_discard)(
                channels.linkhelper_group_name(self.ip_hash),
                self.channel_name
            )

    @catch_all
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        LOGGER.debug(f"LinkHelperConsumer: received {text_data}")
        (msg, ref, data) = json.loads(text_data or '')

        if msg == 'query_response':
            assert ref
            serializer = LinkHelperQueryResponseSerializer(data=data)
            if not serializer.is_valid():
                LOGGER.error(f"LinkHelperConsumer[{self.ip_hash}]: invalid device info ({serializer})")
                return

            cache.insert_linkhelper_query_response(
                ip_hash=self.ip_hash,
                ref=ref,
                device_id=self.device_id,
                device_info=serializer.validated_data,
            )

    @catch_all
    def query_message(self, event):
        LOGGER.debug(f"LinkHelperConsumer: query event ({event})")
        ip_hash, ref = event['ip_hash'], event['ref']
        if self.ip_hash != ip_hash:
            # we check this to avoid very ugly bugs,
            # without another bug this is impossible
            raise Exception("LinkHelperConsumer: ip_hash mismatch")

        self.send(text_data=json.dumps(('query', ref, {})))

    @catch_all
    def verify_code_message(self, event):
        ip_hash, device_id, code = event['ip_hash'], event['device_id'], event['code']
        if self.ip_hash != ip_hash:
            # we check this to avoid very ugly bugs,
            # without another bug this is impossible
            raise Exception("LinkHelperConsumer: ip_hash mismatch")

        if device_id != self.device_id:
            # np, its not meant for this connection
            return

        self.send(text_data=json.dumps(('verify_code', None, {'device_id': device_id, 'code': code})))

    def get_client_ip(self) -> str:
        scope = self.scope
        headers = {k: v for (k, v) in scope['headers']}
        ip = headers.get(b'x-real-ip', b'').decode()

        if ip:
            return ip

        try:
            ip = scope['client'][0]
            return ip
        except (KeyError, IndexError):
            pass

        raise Exception("cannot find out real ip")


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
        data['print.current'] = model_to_dict(printer.current_print) if printer.current_print else None

        from raven import Client
        c = Client(
            install_sys_hook=False,
            install_logging_hook=False,
            enable_breadcrumbs=False,
            tags={
                'printer_id': printer.id,
                'ext_id': ext_id,
                'connected_at': self.connected_at,
                'comeback': comeback,
                'ex': ex
            }
        )
        c.extra_context(data=data)
        c.captureMessage('Resurrected print')
