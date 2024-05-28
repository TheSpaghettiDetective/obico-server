---
title: Websocket
---

## TBD {#tbd}


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