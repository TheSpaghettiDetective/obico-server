---
title: Websocket
---

##  General message schema

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
          "is_nozzle_camera": false,
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

## Sections of the websocket message

### `current_print_ts`

- Timestamp for when current print job starts. This value must maintain consistent for the entire print. Otherwise the server will identify the current print job as a new one.

### `event`

- **`event_type`**: Type of event occurring. One of these values: `PrintStarted|PrintResumed|PrintPaused|PrintDone|PrintFailed`.

### `settings`

- **`webcams`**: List of webcam settings
  - **`name`**: Name of the webcam
  - **`is_primary_camera`**: Indicates if this is the primary camera
  - **`is_nozzle_camera`**: Indicates if this is a nozzle camera
  - **`stream_mode`**: Mode of the stream (e.g., live, recorded)
  - **`stream_id`**: ID of the stream
  - **`flipV`**: Vertical flip of the video stream
  - **`flipH`**: Horizontal flip of the video stream
  - **`rotation`**: Rotation angle of the video stream
  - **`streamRatio`**: Aspect ratio of the video stream

- **`temperature`**: List of temperature profiles

- **`agent`**: Information about the agent managing the print
  - **`name`**: Name of the agent
  - **`version`**: Version of the agent software

### `status`

- **`_ts`**: Timestamp of when the status is collected. This is used to de-dup the status message on the server side, and make sure the latest status message will always win, even if an out-of-date status message is sent to the server later because of transition delays.

- **`state`**: Current state of the printer
  - **`text`**: Textual description of the printer state. One of these values: `Operational|G-Code Downloading|Printing|Pausing|Paused|Cancelling|Offline`.
  - **`flags`**: State flags indicating various statuses
    - **`operational`**: Printer is operational
    - **`printing`**: Printer is printing
    - **`cancelling`**: Print job is being cancelled
    - **`pausing`**: Print job is being paused
    - **`resuming`**: Print job is resuming
    - **`finishing`**: Print job is finishing
    - **`paused`**: Printer is paused

- **`currentLayerHeight`**: Current height of the print layer
- **`currentZ`**: Current Z position of the print head
- **`currentFeedRate`**: Current feed rate of the print
- **`currentFlowRate`**: Current flow rate of the print
- **`currentFanSpeed`**: Current speed of the cooling fan

- **`job`**: Information about the current print job
  - **`file`**: Details of the file being printed
    - **`name`**: Name of the file
    - **`path`**: Path to the file
    - **`display`**: Display name of the file
    - **`origin`**: Origin of the file (e.g., local, SD card)
    - **`size`**: Size of the file in bytes
    - **`date`**: Date of the file
  - **`estimatedPrintTime`**: Estimated time to complete the print job
  - **`averagePrintTime`**: Average time to complete similar print jobs
  - **`lastPrintTime`**: Time taken to complete the last print job
  - **`filament`**: Filament usage details
    - **`tool0`**: Filament used by tool 0
      - **`length`**: Length of filament used
      - **`volume`**: Volume of filament used
  - **`user`**: User who initiated the print job

- **`progress`**: Progress of the print job
  - **`completion`**: Percentage of completion
  - **`filepos`**: Current file position in bytes
  - **`printTime`**: Time elapsed since the start of the print job
  - **`printTimeLeft`**: Estimated time remaining to complete the print job
  - **`printTimeLeftOrigin`**: Origin of the print time left estimation

- **`temperatures`**: Temperature readings
  - **`tool0`**: Temperature of tool 0
    - **`actual`**: Actual temperature
    - **`target`**: Target temperature
    - **`offset`**: Temperature offset
  - **`bed`**: Temperature of the print bed
    - **`actual`**: Actual temperature
    - **`target`**: Target temperature
    - **`offset`**: Temperature offset
  - **`chamber`**: Temperature of the print chamber
    - **`actual`**: Actual temperature
    - **`target`**: Target temperature
    - **`offset`**: Temperature offset

- **`file_metadata`**: Metadata about the file being printed
  - **`hash`**: Hash of the file
  - **`obico`**: Obico-specific metadata
    - **`totalLayerCount`**: Total number of layers
  - **`analysis`**: Analysis of the file
    - **`printingArea`**: Dimensions of the printing area
      - **`maxX`**: Maximum X coordinate
      - **`maxY`**: Maximum Y coordinate
      - **`maxZ`**: Maximum Z coordinate
      - **`minX`**: Minimum X coordinate
      - **`minY`**: Minimum Y coordinate
      - **`minZ`**: Minimum Z coordinate
    - **`dimensions`**: Dimensions of the object
      - **`depth`**: Depth of the object
      - **`height`**: Height of the object
      - **`width`**: Width of the object
    - **`travelArea`**: Dimensions of the travel area
      - **`maxX`**: Maximum X coordinate
      - **`maxY`**: Maximum Y coordinate
      - **`maxZ`**: Maximum Z coordinate
      - **`minX`**: Minimum X coordinate
      - **`minY`**: Minimum Y coordinate
      - **`minZ`**: Minimum Z coordinate
    - **`travelDimensions`**: Dimensions of the travel path
      - **`depth`**: Depth of the travel path
      - **`height`**: Height of the travel path
      - **`width`**: Width of the travel path
    - **`estimatedPrintTime`**: Estimated print time from analysis
    - **`filament`**: Filament usage details from analysis
      - **`tool0`**: Filament used by tool 0
        - **`length`**: Length of filament used
        - **`volume`**: Volume of filament used
  - **`history`**: Print job history
    - **`timestamp`**: Timestamp of the history record
    - **`printTime`**: Print time recorded in history
    - **`success`**: Indicates if the print was successful
    - **`printerProfile`**: Profile of the printer used
  - **`statistics`**: Print job statistics
    - **`averagePrintTime`**: Average print time
    - **`lastPrintTime`**: Last recorded print time


## Example when a printer is printing

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

## Printing state transition

### Printer transitions from idle to printing

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

### Printer transitions from printing to canceled

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
