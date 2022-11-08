from typing import NewType, Dict
from app.models import PrinterEvent

NotificationType = NewType('NotificationType', str)

PrintStarted = NotificationType('PrintStarted',)
PrintDone = NotificationType('PrintDone')
PrintCancelled = NotificationType('PrintCancelled')
PrintPaused = NotificationType('PrintPaused')
PrintResumed = NotificationType('PrintResumed')
FilamentChange = NotificationType('FilamentChange')
HeaterCooledDown = NotificationType('HeaterCooledDown')
HeaterTargetReached = NotificationType('HeaterTargetReached')

OTHER_PRINT_EVENT_MAP = {
  PrinterEvent.STARTED: PrintStarted,
  PrinterEvent.PAUSED: PrintPaused,
  PrinterEvent.RESUMED: PrintResumed,
}

def from_print_event(print_event):
  if print_event.event_type == PrinterEvent.ENDED:
    return PrintCancelled if print_event.print.is_canceled() else PrintDone

  if print_event.event_type == PrinterEvent.FILAMENT_CHANGE:
    return FilamentChange

  return OTHER_PRINT_EVENT_MAP.get(print_event.event_type)
