---
title: Websocket
---

# General message schema
```json
{
  "status": {
    "state": {
      "text": "",
      "flags": {
        "operational": false,
        "printing": false,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "closedOrError": false,
        "error": false,
        "paused": false,
        "ready": false,
        "sdReady": false
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "",
        "path": "",
        "display": "",
        "origin": "",
        "size": 0,
        "date": ""
      },
      "estimatedPrintTime": 0,
      "averagePrintTime": 0,
      "lastPrintTime": 0,
      "filament": {
        "tool0": {
          "length": 0,
          "volume": 0
        }
      },
      "user": ""
    },
    "currentZ": 0,
    "progress": {
      "completion": 0,
      "filepos": 0,
      "printTime": 0,
      "printTimeLeft": 0,
      "printTimeLeftOrigin": ""
    },
    "offsets": {},
    "resends": {
      "count": 0,
      "transmitted": 0,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 0,
        "target": 0,
        "offset": 0
      },
      "bed": {
        "actual": 0,
        "target": 0,
        "offset": 0
      },
      "chamber": {
        "actual": 0,
        "target": 0,
        "offset": 0
      }
    },
    "_ts": 0,
    "currentLayerHeight": 0,
    "file_metadata": {
      "hash": "",
      "obico": {
        "totalLayerCount": 0
      },
      "analysis": {
        "printingArea": {
          "maxX": 0,
          "maxY": 0,
          "maxZ": 0,
          "minX": 0,
          "minY": 0,
          "minZ": 0
        },
        "dimensions": {
          "depth": 0,
          "height": 0,
          "width": 0
        },
        "travelArea": {
          "maxX": 0,
          "maxY": 0,
          "maxZ": 0,
          "minX": 0,
          "minY": 0,
          "minZ": 0
        },
        "travelDimensions": {
          "depth": 0,
          "height": 0,
          "width": 0
        },
        "estimatedPrintTime": 0,
        "filament": {
          "tool0": {
            "length": 0,
            "volume": 0
          }
        }
      },
      "history": {
        "timestamp": "",
        "printTime": 0,
        "success": false,
        "printerProfile": ""
      },
      "statistics": {
        "averagePrintTime": 0,
        "lastPrintTime": 0
      }
    },
    "current_print_ts": 0,
    "event": {
      "event_type": "",
      "data": {
        "state_id": "",
        "state_string": ""
      }
    }
  }
}
```
# Pausing print example
```json
{
  "status": {
    "state": {
      "text": "Pausing",
      "flags": {
        "operational": true,
        "printing": true,
        "cancelling": false,
        "pausing": true,
        "resuming": false,
        "finishing": false,
        "closedOrError": false,
        "error": false,
        "paused": false,
        "ready": false,
        "sdReady": true
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "display": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "date": 1716892098,
        "obico_g_code_file_id": 2
      },
      "estimatedPrintTime": 14830.71632999596,
      "averagePrintTime": null,
      "lastPrintTime": null,
      "filament": {
        "tool0": {
          "length": 10177.899699993939,
          "volume": 0.0
        }
      },
      "user": "user_example"
    },
    "currentZ": 3.45,
    "progress": {
      "completion": 5.315271521675555,
      "filepos": 354053,
      "printTime": 116,
      "printTimeLeft": 2068,
      "printTimeLeftOrigin": "linear"
    },
    "offsets": {},
    "resends": {
      "count": 5,
      "transmitted": 11981,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 220.0,
        "target": 220.0,
        "offset": 0
      },
      "bed": {
        "actual": 90.0,
        "target": 90.0,
        "offset": 0
      },
      "chamber": {
        "actual": null,
        "target": null,
        "offset": 0
      }
    },
    "_ts": 1716904915,
    "currentLayerHeight": 23,
    "file_metadata": {
      "hash": "2a85626157e60f5df7a7cb2e4fd5a8d9fb838265",
      "obico": {
        "totalLayerCount": 608
      },
      "analysis": {
        "printingArea": {
          "maxX": 139.613,
          "maxY": 144.25,
          "maxZ": 91.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "dimensions": {
          "depth": 147.25,
          "height": 91.05,
          "width": 139.613
        },
        "travelArea": {
          "maxX": 139.613,
          "maxY": 200.0,
          "maxZ": 92.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "travelDimensions": {
          "depth": 203.0,
          "height": 92.05,
          "width": 139.613
        },
        "estimatedPrintTime": 14830.71632999596,
        "filament": {
          "tool0": {
            "length": 10177.899699993939,
            "volume": 0.0
          }
        }
      }
    },
    "current_print_ts": 1716904799,
    "event": {
      "event_type": "PrintPaused",
      "data": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "position": {
          "z": 3.45,
          "x": 120.614,
          "e": 0.1896,
          "f": 1812.0,
          "t": 0,
          "y": 71.05
        },
        "owner": "user_example",
        "user": "user_example"
      }
    }
  }
}
```
# Paused print example
```json
{
  "status": {
    "state": {
      "text": "Paused",
      "flags": {
        "operational": true,
        "printing": false,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "closedOrError": false,
        "error": false,
        "paused": true,
        "ready": false,
        "sdReady": true
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "display": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "date": 1716892098,
        "obico_g_code_file_id": 2
      },
      "estimatedPrintTime": 14830.71632999596,
      "averagePrintTime": null,
      "lastPrintTime": null,
      "filament": {
        "tool0": {
          "length": 10177.899699993939,
          "volume": 0.0
        }
      },
      "user": "user_example"
    },
    "currentZ": 3.45,
    "progress": {
      "completion": 5.315271521675555,
      "filepos": 354053,
      "printTime": 116,
      "printTimeLeft": 2068,
      "printTimeLeftOrigin": "linear"
    },
    "offsets": {},
    "resends": {
      "count": 5,
      "transmitted": 11981,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 220.0,
        "target": 220.0,
        "offset": 0
      },
      "bed": {
        "actual": 90.0,
        "target": 90.0,
        "offset": 0
      },
      "chamber": {
        "actual": null,
        "target": null,
        "offset": 0
      }
    },
    "_ts": 1716904976,
    "currentLayerHeight": 23,
    "file_metadata": {
      "hash": "2a85626157e60f5df7a7cb2e4fd5a8d9fb838265",
      "obico": {
        "totalLayerCount": 608
      },
      "analysis": {
        "printingArea": {
          "maxX": 139.613,
          "maxY": 144.25,
          "maxZ": 91.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "dimensions": {
          "depth": 147.25,
          "height": 91.05,
          "width": 139.613
        },
        "travelArea": {
          "maxX": 139.613,
          "maxY": 200.0,
          "maxZ": 92.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "travelDimensions": {
          "depth": 203.0,
          "height": 92.05,
          "width": 139.613
        },
        "estimatedPrintTime": 14830.71632999596,
        "filament": {
          "tool0": {
            "length": 10177.899699993939,
            "volume": 0.0
          }
        }
      }
    },
    "current_print_ts": 1716904799,
    "event": {
      "event_type": "PrintPaused",
      "data": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "position": {
          "z": 3.45,
          "x": 120.614,
          "e": 0.1896,
          "f": 1812.0,
          "t": 0,
          "y": 71.05
        },
        "owner": "user_example",
        "user": "user_example"
      }
    }
  }
}

```
# Printing example
```json
{
  "status": {
    "state": {
      "text": "Printing",
      "flags": {
        "operational": true,
        "printing": true,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "closedOrError": false,
        "error": false,
        "paused": false,
        "ready": false,
        "sdReady": true
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "display": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "date": 1716892098,
        "obico_g_code_file_id": 2
      },
      "estimatedPrintTime": 14830.71632999596,
      "averagePrintTime": null,
      "lastPrintTime": null,
      "filament": {
        "tool0": {
          "length": 10177.899699993939,
          "volume": 0.0
        }
      },
      "user": "user_example"
    },
    "currentZ": 2.2,
    "progress": {
      "completion": 3.5100911988076353,
      "filepos": 233809,
      "printTime": 101,
      "printTimeLeft": 2791,
      "printTimeLeftOrigin": "linear"
    },
    "offsets": {},
    "resends": {
      "count": 5,
      "transmitted": 7809,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 220.0,
        "target": 220.0,
        "offset": 0
      },
      "bed": {
        "actual": 90.0,
        "target": 90.0,
        "offset": 0
      },
      "chamber": {
        "actual": null,
        "target": null,
        "offset": 0
      }
    },
    "_ts": 1716904901,
    "currentLayerHeight": 12,
    "file_metadata": {
      "hash": "2a85626157e60f5df7a7cb2e4fd5a8d9fb838265",
      "obico": {
        "totalLayerCount": 608
      },
      "analysis": {
        "printingArea": {
          "maxX": 139.613,
          "maxY": 144.25,
          "maxZ": 91.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "dimensions": {
          "depth": 147.25,
          "height": 91.05,
          "width": 139.613
        },
        "travelArea": {
          "maxX": 139.613,
          "maxY": 200.0,
          "maxZ": 92.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "travelDimensions": {
          "depth": 203.0,
          "height": 92.05,
          "width": 139.613
        },
        "estimatedPrintTime": 14830.71632999596,
        "filament": {
          "tool0": {
            "length": 10177.899699993939,
            "volume": 0.0
          }
        }
      }
    },
    "current_print_ts": 1716904799
  }
}

```
# Canceling print example
```json
{
  "status": {
    "state": {
      "text": "Cancelling",
      "flags": {
        "operational": true,
        "printing": true,
        "cancelling": true,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "closedOrError": false,
        "error": false,
        "paused": false,
        "ready": false,
        "sdReady": true
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "display": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
        "origin": "local",
        "size": 6661052,
        "date": 1716892098,
        "obico_g_code_file_id": 2
      },
      "estimatedPrintTime": 14830.71632999596,
      "averagePrintTime": null,
      "lastPrintTime": null,
      "filament": {
        "tool0": {
          "length": 10177.899699993939,
          "volume": 0.0
        }
      },
      "user": "user_example"
    },
    "currentZ": null,
    "progress": {
      "completion": null,
      "filepos": null,
      "printTime": null,
      "printTimeLeft": null,
      "printTimeLeftOrigin": null
    },
    "offsets": {},
    "resends": {
      "count": 5,
      "transmitted": 18027,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 220.0,
        "target": 0.0,
        "offset": 0
      },
      "bed": {
        "actual": 90.0,
        "target": 0.0,
        "offset": 0
      },
      "chamber": {
        "actual": null,
        "target": null,
        "offset": 0
      }
    },
    "_ts": 1716906394,
    "currentLayerHeight": 44,
    "file_metadata": {
      "hash": "2a85626157e60f5df7a7cb2e4fd5a8d9fb838265",
      "obico": {
        "totalLayerCount": 608
      },
      "analysis": {
        "printingArea": {
          "maxX": 139.613,
          "maxY": 144.25,
          "maxZ": 91.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "dimensions": {
          "depth": 147.25,
          "height": 91.05,
          "width": 139.613
        },
        "travelArea": {
          "maxX": 139.613,
          "maxY": 200.0,
          "maxZ": 92.05,
          "minX": 0.0,
          "minY": -3.0,
          "minZ": 0.0
        },
        "travelDimensions": {
          "depth": 203.0,
          "height": 92.05,
          "width": 139.613
        },
        "estimatedPrintTime": 14830.71632999596,
        "filament": {
          "tool0": {
            "length": 10177.899699993939,
            "volume": 0.0
          }
        }
      },
      "history": [
        {
          "timestamp": 1716906394.4987602,
          "success": false,
          "printerProfile": "_default"
        }
      ],
      "statistics": {
        "averagePrintTime": {},
        "lastPrintTime": {}
      }
    },
    "current_print_ts": 1716904799
  },
  "event": {
    "event_type": "PrintCancelling",
    "data": {
      "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
      "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
      "origin": "local",
      "size": 6661052,
      "owner": "user_example",
      "user": "user_example"
    }
  }
}

```
# Finishing print example
```json
{
  "status": {
    "state": {
      "text": "Finishing",
      "flags": {
        "operational": true,
        "printing": true,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": true,
        "closedOrError": false,
        "error": false,
        "paused": false,
        "ready": false,
        "sdReady": true
      },
      "error": ""
    },
    "job": {
      "file": {
        "name": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
        "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
        "display": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
        "origin": "local",
        "size": 1090603,
        "date": 1715889035,
        "obico_g_code_file_id": 1
      },
      "estimatedPrintTime": 1254.4362984387842,
      "averagePrintTime": 134.169091964143,
      "lastPrintTime": 127.6107751030031,
      "filament": {
        "tool0": {
          "length": 2195.206300000019,
          "volume": 5.280089926164226
        }
      },
      "user": "alielshimy"
    },
    "currentZ": 35.0,
    "progress": {
      "completion": 100.0,
      "filepos": 1090603,
      "printTime": 119,
      "printTimeLeft": 0,
      "printTimeLeftOrigin": null
    },
    "offsets": {},
    "resends": {
      "count": 8,
      "transmitted": 56826,
      "ratio": 0
    },
    "temperatures": {
      "tool0": {
        "actual": 210.0,
        "target": 0.0,
        "offset": 0
      },
      "bed": {
        "actual": 60.0,
        "target": 0.0,
        "offset": 0
      },
      "chamber": {
        "actual": null,
        "target": null,
        "offset": 0
      }
    },
    "_ts": 1716907533,
    "currentLayerHeight": 25,
    "file_metadata": {
      "hash": "51217e1b15009326146f76a3390ed81d97f480aa",
      "obico": {
        "totalLayerCount": 26
      },
      "analysis": {
        "printingArea": {
          "maxX": 170.0,
          "maxY": 122.313,
          "maxZ": 5.0,
          "minX": 40.0,
          "minY": -2.0,
          "minZ": 0.0
        },
        "dimensions": {
          "depth": 124.313,
          "height": 5.0,
          "width": 130.0
        },
        "travelArea": {
          "maxX": 179.0,
          "maxY": 178.0,
          "maxZ": 35.0,
          "minX": 0.0,
          "minY": -2.0,
          "minZ": 0.0
        },
        "travelDimensions": {
          "depth": 180.0,
          "height": 35.0,
          "width": 179.0
        },
        "estimatedPrintTime": 1254.4362984387842,
        "filament": {
          "tool0": {
            "length": 2195.206300000019,
            "volume": 5.280089926164226
          }
        }
      },
      "history": [
        {
          "timestamp": 1715889179.3695226,
          "printTime": 130.96288251300575,
          "success": true,
          "printerProfile": "_default"
        },
                  .
                  .
                  .
      ],
      "statistics": {
        "averagePrintTime": {
          "_default": 133.1707976056669
        },
        "lastPrintTime": {
          "_default": 119.1946765870016
        }
      }
    },
    "current_print_ts": 1716907414
  },
  "event": {
    "event_type": "PrinterStateChanged",
    "data": {
      "state_id": "FINISHING",
      "state_string": "Finishing"
    }
  }
}

```
# Other schemas to review - delete them if we do not need them
### Print Job Selected
#### Event: PrintJobSelected

#### Payload:

origin: The origin of the print job (e.g., 'local').
path: The file path of the selected print job.
owner: The owner of the print job.
user: The user who selected the print job.
Example:

```json
{
  "origin": "local",
  "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "owner": "username",
  "user": "username"
}
```

### File Removed
#### Event: FileRemoved

#### Payload:

storage: The storage location of the file (e.g., 'local').
path: The file path of the removed file.
name: The name of the removed file.
type: An array indicating the type of the file (e.g., ['machinecode', 'gcode']).
Example:

```json
{
  "storage": "local",
  "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
  "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
  "type": ["machinecode", "gcode"]
}
```

### File Added
#### Event: FileAdded

#### Payload:

storage: The storage location of the file (e.g., 'local').
path: The file path of the added file.
name: The name of the added file.
type: An array indicating the type of the file (e.g., ['machinecode', 'gcode']).
operation: The operation performed (e.g., 'add').
Example:

```json
{
  "storage": "local",
  "path": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
  "name": "temp-tower-220-260_petg_mk3s_4h_34m.gcode",
  "type": ["machinecode", "gcode"],
  "operation": "add"
}
```

### File Selected
#### Event: FileSelected

#### Payload:

name: The name of the selected file.
path: The file path of the selected file.
origin: The origin of the selected file (e.g., 'local').
size: The size of the selected file.
owner: The owner of the selected file.
user: The user who selected the file.
Example:

```json
{
  "name": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "origin": "local",
  "size": null,
  "owner": "username",
  "user": "username"
}
```

### Printer State Changed
#### Event: PrinterStateChanged

#### Payload:

state_id: The new state ID (e.g., 'STARTING').
state_string: The new state string (e.g., 'Starting').
Example:

```json
{
  "state_id": "STARTING",
  "state_string": "Starting"
}
```

6. Print Started
#### Event: PrintStarted

#### Payload:

name: The name of the print job file.
path: The file path of the print job.
origin: The origin of the print job (e.g., 'local').
size: The size of the print job file.
owner: The owner of the print job.
user: The user who started the print job.
Example:

```json
{
  "name": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "origin": "local",
  "size": 1090603,
  "owner": "username",
  "user": "username"
}
```

### Chart Marked
#### Event: ChartMarked

#### Payload:

type: The type of chart mark (e.g., 'print').
label: The label of the chart mark (e.g., 'Start').
Example:

```json
{
  "type": "print",
  "label": "Start"
}
```

### Gcode Script Before Print Started Running
#### Event: GcodeScriptBeforePrintStartedRunning

#### Payload:

name: The name of the Gcode script.
path: The file path of the Gcode script.
origin: The origin of the Gcode script (e.g., 'local').
size: The size of the Gcode script file.
owner: The owner of the Gcode script.
user: The user who initiated the Gcode script.
Example:

```json
{
  "name": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "origin": "local",
  "size": 1090603,
  "owner": "username",
  "user": "username"
}
```

### Gcode Script Before Print Started Finished
#### Event: GcodeScriptBeforePrintStartedFinished

#### Payload:

name: The name of the Gcode script.
path: The file path of the Gcode script.
origin: The origin of the Gcode script (e.g., 'local').
size: The size of the Gcode script file.
owner: The owner of the Gcode script.
user: The user who initiated the Gcode script.
Example:

```json
{
  "name": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "path": "PYC3D-SONIC-HEAD-KEYCHAIN.gcode",
  "origin": "local",
  "size": 1090603,
  "owner": "username",
  "user": "username"
}
```

### Z Change
#### Event: ZChange

#### Payload:

new: The new Z position.
old: The previous Z position.
Example:

```json
{
  "new": 0.4,
  "old": 0.2
}