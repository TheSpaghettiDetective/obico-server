from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from channels_presence.models import Room
from django.dispatch import receiver
from channels_presence.signals import presence_changed

from . import cache

def octo_group_name(printer_id):
    return 'p_octo.{}'.format(printer_id)

def web_group_name(printer_id):
    return 'p_web.{}'.format(printer_id)

def janus_web_group_name(printer_id):
    return 'janus_web.{}'.format(printer_id)


def octoprinttunnel_group_name(printer_id):
    return 'octoprinttunnel.{}'.format(printer_id)


def send_msg_to_printer(printer_id, msg_dict):
    msg_dict.update({
        'type': 'printer.message',  # mapped to -> printer_message in consumer
    })
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        octo_group_name(printer_id),
        msg_dict,
    )

def send_message_to_web(printer_id, msg_dict):
    msg_dict.update({'type': 'web.message'})    # mapped to -> web_message in consumer
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        web_group_name(printer_id),
        msg_dict,
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


def send_message_to_octoprinttunnel(group_name, data):
    msg_dict = {
        # mapped to -> octoprinttunnel_message in consumer
        'type': 'octoprinttunnel.message',
        'data': data
    }
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        group_name,
        msg_dict,
    )


@receiver(presence_changed)
def broadcast_ws_connection_change(sender, room, **kwargs):
    (group, printer_id) = room.channel_name.split('.')  # room.channel_name is actually the room name (= group name)
    if group == 'p_web':
        send_msg_to_printer(printer_id, {'remote_status': {'viewing': room.get_anonymous_count() > 0}})
    if group == 'p_octo':
        if num_ws_connections(octo_group_name(printer_id)) <= 0:
            cache.printer_status_delete(printer_id)
        send_status_to_web(printer_id)


def num_ws_connections(group_name):
    rooms = Room.objects.filter(channel_name=group_name)      # room.channel_name is actually the room name (= group name)
    return rooms[0].get_anonymous_count() if len(rooms) > 0 else 0
