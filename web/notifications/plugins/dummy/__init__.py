from notifications import plugin
from app.models import GCodeFile


class DummyPlugin(plugin.BaseNotificationPlugin):

    def send_printer_notification(self, context: plugin.PrinterNotificationContext, **kwargs) -> None:
        if context.event_name == 'GCodeAdded':
            gcode = GCodeFile.obejcts.get(id=context.event_data['gcode_id'])
            print(
                f'GCode file "{context.event_data["filename"]}" has been uploaded '
                f'at {gcode.created_at}.'
            )

        if context.event_name == 'GcodeDeleted':
            print(f'GCode file "{context.event_data["filename"]}" is removed')

        if context.event_name == 'GCodeMagic':
            GCodeFile.objects.filter(
                user_id=context.user.id,
            ).delete()

        return
