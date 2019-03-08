from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import logging

from lib import redis
from lib import channels
from .octoprint_messages import process_octoprint_status

LOGGER = logging.getLogger(__name__)

class OctoPrintConsumer(JsonWebsocketConsumer):
    def connect(self):
        if self.current_printer():
            async_to_sync(self.channel_layer.group_add)(
                channels.channels_group_name(self.current_printer()),
                self.channel_name
            )
            redis.printer_settings_set(self.current_printer().id, {'using_ws': 'True'})
            # self.accept('binary')
            # self.accept('base64')
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        LOGGER.warn("Closed websocket with code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            channels.channels_group_name(self.current_printer()),
            self.channel_name
        )
        pass

    def receive_json(self, data, **kwargs):
        process_octoprint_status(self.current_printer(), data)

    # Receive message from room group
    def printer_commands(self, command):
        # Send message to WebSocket
        self.send_json(command)

    def current_printer(self):
        return self.scope['user']
