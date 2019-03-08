from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import redis
from app.models import *

def channels_group_name(printer):
    return 'printer_{}'.format(printer.id)

def send_commands_to_channel(printer):
    if not redis.printer_settings_get(printer.id, 'using_ws'):
        return

    commands = PrinterCommand.objects.filter(printer=printer, status=PrinterCommand.PENDING)
    commands.update(status=PrinterCommand.SENT)

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        channels_group_name(printer),
        {
            'type': 'printer_commands',
            'commands': [ json.loads(c.command) for c in commands ],
        }
    )
