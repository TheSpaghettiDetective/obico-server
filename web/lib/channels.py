from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import time
from django.dispatch import receiver

from . import cache

CHANNEL_CONSIDERED_ALIVE_IF_TOUCHED_IN_SECS = 1200


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


def broadcast_ws_connection_change(group_name):
    (group, printer_id) = group_name.split('.')
    if group == 'p_web':
        send_viewing_status(printer_id, get_num_ws_connections(group_name))
    if group == 'p_octo':
        if get_num_ws_connections(group_name) <= 0:
            cache.printer_status_delete(printer_id)
        send_status_to_web(printer_id)


def send_viewing_status(printer_id, viewing_count=None):
    if viewing_count is None:
        viewing_count = get_num_ws_connections(web_group_name(printer_id))

    send_msg_to_printer(printer_id, {'remote_status': {'viewing': viewing_count > 0}})


async def async_get_num_ws_connections(group_name, threshold=None, current_time=None):
    threshold = threshold if threshold is not None else CHANNEL_CONSIDERED_ALIVE_IF_TOUCHED_IN_SECS
    current_time = time.time() if current_time is None else current_time
    chlayer = get_channel_layer()
    async with chlayer.connection(chlayer.consistent_hash(group_name)) as conn:
        return await conn.zcount(
            chlayer._group_key(group_name),
            min=current_time - threshold)

get_num_ws_connections = async_to_sync(async_get_num_ws_connections)


async def touch_channel(group_name, channel_name):
    chlayer = get_channel_layer()
    # group_add adds or updates existing channel in a redis sorted set,
    # and sets current time as score.. just what we need
    await chlayer.group_add(group_name, channel_name)

touch_channel = async_to_sync(touch_channel)
