from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from channels_presence.models import Room
from django.dispatch import receiver
from channels_presence.signals import presence_changed

from . import redis

def octo_group_name(printer_id):
    return 'p_octo.{}'.format(printer_id)

def web_group_name(printer_id):
    return 'p_web.{}'.format(printer_id)

def janus_web_group_name(printer_id):
    return 'janus_web.{}'.format(printer_id)

def send_msg_to_printer(printer_id, msg_dict):
    msg_dict.update({'type': 'printer.message'})    # mapped to -> printer_message in consumer
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        octo_group_name(printer_id),
        msg_dict,
    )

def send_remote_status_to_printer(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        octo_group_name(printer_id),
        {
            'type': 'printer.message',    # mapped to -> printer_message in consumer
            'remote_status': msg
        }
    )

def send_status_to_web(printer_id):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        web_group_name(printer_id),
        {
            'type': 'printer.status',         # mapped to -> printer_status in consumer
        }
    )

def send_janus_to_web(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        janus_web_group_name(printer_id),
        {
            'type': 'janus.message',         # mapped to -> janus_message in consumer
            'msg': msg,
        }
    )

@receiver(presence_changed)
def broadcast_ws_connection_change(sender, room, **kwargs):
    (group, printer_id) = room.channel_name.split('.')  # room.channel_name is actually the room name (= group name)
    if group == 'p_web':
        send_viewing_status(printer_id, room.get_anonymous_count())
    if group == 'p_octo':
        if num_ws_connections(octo_group_name(printer_id)) <= 0:
            redis.printer_status_delete(printer_id)
        send_status_to_web(printer_id)

def send_viewing_status(printer_id, viewing_count=None):
    if viewing_count == None:
        viewing_count = num_ws_connections(web_group_name(printer_id))

    send_msg_to_printer(printer_id, {'remote_status': {'viewing': viewing_count > 0}})

def num_ws_connections(group_name):
    rooms = Room.objects.filter(channel_name=group_name)      # room.channel_name is actually the room name (= group name)
    return rooms[0].get_anonymous_count() if len(rooms) > 0 else 0
