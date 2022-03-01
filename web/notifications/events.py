from typing import NewType, Dict

PrinterEvent = NewType('PrinterEvent', str)
__PRINTER_EVENTS: Dict[str, PrinterEvent] = {}


def _printer_event(name: str, store: Dict = __PRINTER_EVENTS) -> PrinterEvent:
    event = PrinterEvent(name)
    assert name not in store
    store[name] = event
    return event


def is_supported(name: str, store: Dict = __PRINTER_EVENTS) -> bool:
    return name in store


PrintStarted = _printer_event('PrintStarted',)
PrintFailed = _printer_event('PrintFailed')
PrintDone = _printer_event('PrintDone')
PrintCancelled = _printer_event('PrintCancelled')
PrintPaused = _printer_event('PrintPaused')
PrintResumed = _printer_event('PrintResumed')

PrintProgress = _printer_event('PrintProgress')

FilamentChange = _printer_event('FilamentChange')

HeaterCooledDown = _printer_event('HeaterCooledDown')
HeaterTargetReached = _printer_event('HeaterTargetReached')
