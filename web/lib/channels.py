from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import redis
from app.models import *

def commands_group_name(printer_id):
    return 'p_cmd_{}'.format(printer_id)

def status_group_name(printer_id):
    return 'p_sts_{}'.format(printer_id)

def send_commands_to_group(printer_id):
    if not redis.printer_settings_get(printer_id, 'using_ws'):
        return

    commands = PrinterCommand.objects.filter(printer_id=printer_id, status=PrinterCommand.PENDING)
    if not commands:
        return

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.commands',    # mapped to -> printer_commands in consumer
            'commands': [ json.loads(c.command) for c in commands ],
        }
    )

    commands.update(status=PrinterCommand.SENT)

def send_status_to_group(printer_id):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        status_group_name(printer_id),
        {
            'type': 'printer.status',         # mapped to -> printer_status in consumer
        }
    )
