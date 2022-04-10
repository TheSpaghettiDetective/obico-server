from typing import NewType, Dict
from app.models import PrintEvent

NotificationType = NewType('NotificationType', str)

PrintStarted = NotificationType('PrintStarted',)
PrintFailed = NotificationType('PrintFailed')
PrintDone = NotificationType('PrintDone')
PrintCancelled = NotificationType('PrintCancelled')
PrintPaused = NotificationType('PrintPaused')
PrintResumed = NotificationType('PrintResumed')

PrintProgress = NotificationType('PrintProgress')

FilamentChange = NotificationType('FilamentChange')

HeaterCooledDown = NotificationType('HeaterCooledDown')
HeaterTargetReached = NotificationType('HeaterTargetReached')

OTHER_PRINT_EVENT_MAP = {
  PrintEvent.STARTED: PrintStarted,
  PrintEvent.PAUSED: PrintPaused,
  PrintEvent.RESUMED: PrintResumed
}

def from_print_event(print_event):
  if print_event.event_type == PrintEvent.ENDED:
    return PrintCancelled if print_event.print.is_canceled() else PrintDone
  
  return OTHER_PRINT_EVENT_MAP.get(print_event.event_type)
