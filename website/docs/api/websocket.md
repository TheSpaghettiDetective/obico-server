---
title: Websocket
---

##  General message schema {#general-message-schema}

```json
{
  "current_print_ts": "",
  "event": {
    "event_type": "",
  },
  {
    "settings": {
      "webcams": [
        {
          "name": "",
          "is_primary_camera": true,
          "stream_mode": "",
          "stream_id": 1,
          "flipV": false,
          "flipH": false,
          "rotation": 0,
          "streamRatio": "16:9"
        }
      ],
      "temperature": {
        "profiles": []
      },
      "agent": {
        "name": "",
        "version": ""
      }
    }
  },
  "status": {
    "_ts": 0,
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
    "currentLayerHeight": 0,
    "currentZ": 0,
    "currentFeedRate": 1,
    "currentFlowRate": 1,
    "currentFanSpeed": 0
    "progress": {
      "completion": 0,
      "filepos": 0,
      "printTime": 0,
      "printTimeLeft": 0,
      "printTimeLeftOrigin": ""
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
    }
  }
}
```

## Sections of the websocket message {#sections-of-the-websocket-message}

### `current_print_ts` **Required** {#current_print_ts-required}

Timestamp for when current print job starts. This value must maintain consistent for the entire print. Otherwise the server will identify the current print job as a new one.

### `event` **Optional** {#event-optional}

- **`event_type`**: **Required**. Type of event occurring. One of these values: `PrintStarted|PrintResumed|PrintPaused|PrintDone|PrintFailed`.

### `settings` **Optional** {#settings-optional}

- **`webcams`**: **Optional** List of webcam settings
  - **`name`**: **Required** Name of the webcam
  - **`is_primary_camera`**: **Optional** Default to `false`. Indicates if this is the primary camera
  - **`stream_mode`**: **Optional** Mode of the stream (e.g., live, recorded)
  - **`stream_id`**: **Required** ID of the stream for the WebRTC connection
  - **`flipV`**: **Optional** Vertical flip of the video stream
  - **`flipH`**: **Optional** Horizontal flip of the video stream
  - **`rotation`**: **Optional** Rotation angle of the video stream
  - **`streamRatio`**: **Optional** Aspect ratio of the video stream

- **`temperature`**: **Optional** List of temperature profiles

- **`agent`**: **Required** Information about the agent managing the print
  - **`name`**: **Required** Name of the agent
  - **`version`**: **Required** Version of the agent software

### `status` **Required** {#status-required}

- **`_ts`**: **Required** Timestamp of when the status is collected. This is used to de-dup the status message on the server side, and make sure the latest status message will always win, even if an out-of-date status message is sent to the server later because of transition delays.

- **`state`**: **Required** Current state of the printer
  - **`text`**: **Required** Textual description of the printer state. One of these values: `Operational|G-Code Downloading|Printing|Pausing|Paused|Cancelling|Offline`.
  - **`flags`**: **Required** State flags indicating various statuses
    - **`operational`**: **Required** Printer is operational
    - **`printing`**: **Required** Printer is printing
    - **`cancelling`**: **Required** Print job is being cancelled
    - **`pausing`**: **Required** Print job is being paused
    - **`resuming`**: **Required** Print job is resuming
    - **`finishing`**: **Required** Print job is finishing
    - **`paused`**: **Required** Printer is paused

- **`currentLayerHeight`**: **Optional** Current height of the print layer
- **`currentZ`**: **Optional** Current Z position of the print head
- **`currentFeedRate`**: **Optional** Current feed rate of the print
- **`currentFlowRate`**: **Optional** Current flow rate of the print
- **`currentFanSpeed`**: **Optional** Current speed of the cooling fan

- **`job`**: **Optional** Information about the current print job
  - **`file`**: **Required** Details of the file being printed
    - **`name`**: **Required** Name of the file
    - **`path`**: **Required** Path to the file
    - **`display`**: **Required** Display name of the file
    - **`origin`**: **Optional** Origin of the file (e.g., local, SD card)
    - **`size`**: **Optional** Size of the file in bytes
    - **`date`**: **Optional** Date of the file
  - **`estimatedPrintTime`**: **Optional** Estimated time to complete the print job
  - **`averagePrintTime`**: **Optional** Average time to complete similar print jobs
  - **`lastPrintTime`**: **Optional** Time taken to complete the last print job
  - **`filament`**: **Optional** Filament usage details
    - **`tool0`**: **Optional** Filament used by tool 0
      - **`length`**: **Optional** Length of filament used
      - **`volume`**: **Optional** Volume of filament use

- **`progress`**: **Optional** Progress of the print job
  - **`completion`**: **Optional** Percentage of completion
  - **`filepos`**: **Optional** Current file position in bytes
  - **`printTime`**: **Optional** Time elapsed since the start of the print job
  - **`printTimeLeft`**: **Optional** Estimated time remaining to complete the print job

- **`temperatures`**: **Optional** Temperature readings
  - **`tool0`**: **Optional** Temperature of tool 0
    - **`actual`**: **Optional** Actual temperature
    - **`target`**: **Optional** Target temperature
    - **`offset`**: **Optional** Temperature offset
  - **`bed`**: **Optional** Temperature of the print bed
    - **`actual`**: **Optional** Actual temperature
    - **`target`**: **Optional** Target temperature
    - **`offset`**: **Optional** Temperature offset
  - **`chamber`**: **Optional** Temperature of the print chamber
    - **`actual`**: **Optional** Actual temperature
    - **`target`**: **Optional** Target temperature
    - **`offset`**: **Optional** Temperature offset

- **`file_metadata`**: **Optional** Metadata about the file being printed
  - **`hash`**: **Optional** Hash of the file
  - **`obico`**: **Optional** Obico-specific metadata
    - **`totalLayerCount`**: **Optional** Total number of layers
  - **`analysis`**: **Optional** Analysis of the file
    - **`printingArea`**: **Optional** Dimensions of the printing area
      - **`maxX`**: **Optional** Maximum X coordinate
      - **`maxY`**: **Optional** Maximum Y coordinate
      - **`maxZ`**: **Optional** Maximum Z coordinate
      - **`minX`**: **Optional** Minimum X coordinate
      - **`minY`**: **Optional** Minimum Y coordinate
      - **`minZ`**: **Optional** Minimum Z coordinate
    - **`dimensions`**: **Optional** Dimensions of the object
      - **`depth`**: **Optional** Depth of the object
      - **`height`**: **Optional** Height of the object
      - **`width`**: **Optional** Width of the object
    - **`travelArea`**: **Optional** Dimensions of the travel area
      - **`maxX`**: **Optional** Maximum X coordinate
      - **`maxY`**: **Optional** Maximum Y coordinate
      - **`maxZ`**: **Optional** Maximum Z coordinate
      - **`minX`**: **Optional** Minimum X coordinate
      - **`minY`**: **Optional** Minimum Y coordinate
      - **`minZ`**: **Optional** Minimum Z coordinate
    - **`travelDimensions`**: **Optional** Dimensions of the travel path
      - **`depth`**: **Optional** Depth of the travel path
      - **`height`**: **Optional** Height of the travel path
      - **`width`**: **Optional** Width of the travel path
    - **`estimatedPrintTime`**: **Optional** Estimated print time from analysis
    - **`filament`**: **Optional** Filament usage details from analysis
      - **`tool0`**: **Optional** Filament used by tool 0
        - **`length`**: **Optional** Length of filament used
        - **`volume`**: **Optional** Volume of filament used
  - **`history`**: **Optional** Print job history
    - **`timestamp`**: **Optional** Timestamp of the history record
    - **`printTime`**: **Optional** Print time recorded in history
    - **`success`**: **Optional** Indicates if the print was successful
    - **`printerProfile`**: **Optional** Profile of the printer used
  - **`statistics`**: **Optional** Print job statistics
    - **`averagePrintTime`**: **Optional** Average print time
    - **`lastPrintTime`**: **Optional** Last recorded print time


## Example when a printer is printing {#example-when-a-printer-is-printing}

```json
{
  "current_print_ts": 1716904799,
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
        "paused": false,
        "ready": false,
      }
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
      }
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
    }
  }
}
```

## Printing state transition {#printing-state-transition}

### Printer transitions from idle to printing {#printer-transitions-from-idle-to-printing}

```json
{
  "current_print_ts": 1716904799,
  "event": {
    "event_type": "PrintStarted",
  },
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
        "paused": false,
        "ready": false,
      },
      ...
    }
  }
}
  ```

### Printer transitions from printing to paused

```json
{
  "current_print_ts": 1716904799,
  "event": {
    "event_type": "PrintPaused",
  },
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
        "paused": true,
        "ready": false,
      },
      ...
    }
  }
}
  ```

### Printer transitions from printing to canceled {#printer-transitions-from-printing-to-canceled}

```json
{
  "current_print_ts": 1716904799,
  "event": {
    "event_type": "PrintCancelled",
  },
  "status": {
    "state": {
      "text": "Operational",
      "flags": {
        "operational": true,
        "printing": false,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "paused": false,
        "ready": false,
      },
      ...
    }
  }
}
  ```


### Printer transitions from printing to finished

```json
{
  "current_print_ts": 1716904799,
  "event": {
    "event_type": "PrintDone",
  },
  "status": {
    "state": {
      "text": "Operational",
      "flags": {
        "operational": true,
        "printing": false,
        "cancelling": false,
        "pausing": false,
        "resuming": false,
        "finishing": false,
        "paused": false,
        "ready": false,
      },
      ...
    }
  }
}
  ```
