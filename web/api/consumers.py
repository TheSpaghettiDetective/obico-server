from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import logging

from lib import redis
from lib import channels
from .octoprint_messages import process_octoprint_status
from app.models import *
from .serializers import *

LOGGER = logging.getLogger(__name__)

class WebConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.printer_id = self.scope['url_route']['kwargs']['printer_id']
        try:
            printer = Printer.objects.get(user=self.current_user(), id=self.printer_id)     # Exception for un-authenticated or un-authorized access

            async_to_sync(self.channel_layer.group_add)(
                channels.status_group_name(self.printer_id),
                self.channel_name
            )
            self.accept()
            channels.send_status_to_group(printer.id)
        except:
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("WebConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.status_group_name(self.printer_id),
            self.channel_name
        )

    def receive_json(self, data, **kwargs):
        pass # This websocket is used only to get status update for now. not receiving anything

    def printer_status(self, data):
        serializer = PrinterSerializer(Printer.objects.get(id=self.printer_id))
        self.send_json(serializer.data)

    def current_user(self):
        return self.scope['user']

class OctoPrintConsumer(JsonWebsocketConsumer):
    def connect(self):
        if self.current_printer().is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                channels.commands_group_name(self.current_printer().id),
                self.channel_name
            )
            redis.printer_settings_set(self.current_printer().id, {'using_ws': 'True'})
            # self.accept('binary')
            # self.accept('base64')
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("OctoPrintConsumer: Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.commands_group_name(self.current_printer().id),
            self.channel_name
        )

    def receive_json(self, data, **kwargs):
        process_octoprint_status(self.current_printer(), data)

    def printer_commands(self, command):
        self.send_json(command)

    def current_printer(self):
        return self.scope['user']
