from notifications import plugin
from app.models import GCodeFile


class DummyPlugin(plugin.BaseNotificationPlugin):

    def send_printer_notification(self, context: plugin.PrinterNotificationContext, **kwargs) -> None:
        if context.notification_type == 'GCodeAdded':
            gcode = GCodeFile.obejcts.get(id=context.notification_data['gcode_id'])
            print(
                f'GCode file "{context.notification_data["filename"]}" has been uploaded '
                f'at {gcode.created_at}.'
            )

        if context.notification_type == 'GcodeDeleted':
            print(f'GCode file "{context.notification_data["filename"]}" is removed')

        if context.notification_type == 'GCodeMagic':
            GCodeFile.objects.filter(
                user_id=context.user.id,
            ).delete()

        return
