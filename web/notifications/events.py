from typing import NewType, Dict

PrinterEvent = NewType('PrinterEvent', str)

PrintStarted = PrinterEvent('PrintStarted',)
PrintFailed = PrinterEvent('PrintFailed')
PrintDone = PrinterEvent('PrintDone')
PrintCancelled = PrinterEvent('PrintCancelled')
PrintPaused = PrinterEvent('PrintPaused')
PrintResumed = PrinterEvent('PrintResumed')

PrintProgress = PrinterEvent('PrintProgress')

FilamentChange = PrinterEvent('FilamentChange')

HeaterCooledDown = PrinterEvent('HeaterCooledDown')
HeaterTargetReached = PrinterEvent('HeaterTargetReached')

OTHER_PRINT_EVENTS = [PrintStarted, PrintPaused, PrintResumed]
