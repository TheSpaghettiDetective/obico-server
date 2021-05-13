from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


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
