from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

from . import redis

def commands_group_name(printer_id):
    return 'p_cmd_{}'.format(printer_id)

def status_group_name(printer_id):
    return 'p_sts_{}'.format(printer_id)

def janus_web_group_name(printer_id):
    return 'janus_web_{}'.format(printer_id)

def send_commands_to_printer(printer_id, cmd):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.message',    # mapped to -> printer_message in consumer
            'commands': [ cmd ],
        }
    )

def send_janus_msg_to_printer(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.message',    # mapped to -> printer_message in consumer
            'janus': msg
        }
    )

def send_remote_status_to_printer(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.message',    # mapped to -> printer_message in consumer
            'remote_status': msg
        }
    )

def send_status_to_web(printer_id):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        status_group_name(printer_id),
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
