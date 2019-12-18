from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import logging
from raven.contrib.django.raven_compat.models import client as sentryClient
from django.core.exceptions import ObjectDoesNotExist
import newrelic.agent

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
                channels.status_group_name(self.printer.id),
                self.channel_name
            )
            self.accept()
            channels.send_status_to_web(self.printer.id)
            send_remote_status(self.printer, viewing=True)
        except:
            LOGGER.exception("Websocket failed to connect")
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("WebConsumer: Closed websocket with code: {}".format(close_code))
        send_remote_status(self.printer, viewing=False)
        async_to_sync(self.channel_layer.group_discard)(
            channels.status_group_name(self.printer.id),
            self.channel_name
        )

    def receive_json(self, data, **kwargs):
        pass # This websocket is used only to get status update for now. not receiving anything

    def printer_status(self, data):
        serializer = PrinterSerializer(Printer.objects.get(id=self.printer.id))
        self.send_json(serializer.data)

    def current_user(self):
        return self.scope['user']

class OctoPrintConsumer(JsonWebsocketConsumer):
    @newrelic.agent.background_task()
    def connect(self):
        if self.current_printer().is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                channels.commands_group_name(self.current_printer().id),
                self.channel_name
            )
            self.accept()
            send_remote_status(self.current_printer())
        else:
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("OctoPrintConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.commands_group_name(self.current_printer().id),
            self.channel_name
        )

    def receive_json(self, data, **kwargs):
        try:
            printer = Printer.objects.get(id=self.current_printer().id)

            if (data.get('janus')):
                channels.send_janus_to_web(self.current_printer().id, data.get('janus'))
            else:
                process_octoprint_status(printer, data)

        except ObjectDoesNotExist:
            import traceback; traceback.print_exc()
            self.close()
        except:  # sentry doesn't automatically capture consumer errors
            import traceback; traceback.print_exc()
            self.close()
            sentryClient.captureException()

    def printer_message(self, command):
        self.send_json(command)

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
        channels.send_janus_msg_to_printer(self.printer.id, text_data)

    def janus_message(self, msg):
        self.send(text_data=msg.get('msg'))
