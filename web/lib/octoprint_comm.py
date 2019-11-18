from . import channels
from app.models import PrinterCommand

def send_commands_to_printer_if_needed(printer_id):
    commands = PrinterCommand.objects.filter(printer_id=printer_id, status=PrinterCommand.PENDING)
    if not commands:
        return
    channels.send_commands_to_printer(printer_id, commands)
    commands.update(status=PrinterCommand.SENT)
