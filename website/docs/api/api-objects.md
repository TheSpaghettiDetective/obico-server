---
title: API Objects
---

## `Printer` {#printer}

An object that represents a printer.

- `id`: ID used in API path. *ReadOnly*
- `name`: Printer name.
- `created_at`: The timestamp when the printer is created. In ISO-8601 format.
- `action_on_failure`: What to do when a possible failure is detected. An `Enum`.
    - `PAUSE`: The print will be paused automatically. Note: when the detection (prediction score) is not very high, the print won't be paused. An alert will be sent instead in this case.
    - `NONE`: No action. Since an alert will always be sent, `NONE` means the user will still receive an alert.
- `watching_enabled`: If the failure detection is enabled by the user. Note: even if the failure detection is enabled, the system may not actively watch a print, for one reason or another. See `not_watching_reason` for details.
- `not_watching_reason`: A textual representation of why a print is not being actively watch.
    - *AI failure detection is disabled*: `watching_enabled` is set to `false`
    - *You have run out of AI Detection Hours*: The `dh_balance` in the [`User`](#user) object is 0 or a negative number.
    - *Printer is not actively printing*: Either `current_print` is `null`, or the printer is paused.
    - *Alerts are muted for current print*: The user has selected "mute alert for the rest of the print".
- `tools_off_on_pause`: Whether or not the tool (hotend) heater should be shut off when a print is paused.
- `bed_off_on_pause`: Whether or not the print bed heater should be shut off when a print is paused.
- `retract_on_pause`: The distance (in mm) the filament should be retracted when a print is paused. No retraction when it's 0.
- `lift_z_on_pause`: The distance (in mm) of the z-lift when a print is paused. No z-lift when it's 0.
- `detective_sensitivity`: The sensitivity for the failure detection. It should be a value between 0.8 (lowest sensitivity) and 1.2 (highest sensitivity).
- `pic`: The most recent webcam image for the printer. An object. Currently it has only 1 property.
    - `img_url`: The url to the image.
- `status`: An [`PrinterStatus`](#printerstatus) object.
- `settings`: An [`PrinterSettings`](#printersettings) object.
- `current_print`: An [`Print] object that represents the current print job of the printer. `Null` when the printer is idle.
- `normalized_p`: A normalized *prediction score* for failure detection. It's a number between 0 and 1. 0 means no failure is detected. 1 means the maximum confidence on predicting a print failure.
- `auth_token`: The token the printer can use to authenticate itself.

## `PrinterStatus` {#printerstatus}

- `state`: A [`State`](#state) object.
- `job`: A [`Job`](#job) object.
- `progress`: A [`JobProgress`](#jobprogress) object.
- `temperatures`: A [`temperatures`](#temperatures) object.

## `State` {#state}

- `text`: A textual representation of the current state of the printer, e.g. “Operational” or “Printing”.
- `flags`: Printer state flags
- `flags.operational``: true if the printer is operational, false otherwise
- `flags.paused`: true if the printer is currently paused, false otherwise
- `flags.printing`: true if the printer is currently printing, false otherwise
- `flags.pausing`: true if the printer is currently printing and in the process of pausing, false otherwise
- `flags.cancelling`: true if the printer is currently printing and in the process of pausing, false otherwise
- `flags.sdReady`: true if the printer’s SD card is available and initialized, false otherwise. This is redundant information to the SD State.
- `flags.error`: true if an unrecoverable error occurred, false otherwise
- `flags.ready`: true if the printer is operational and no data is currently being streamed to SD, so ready to receive instructions
- `flags.closedOrError`: true if the printer is disconnected (possibly due to an error), false otherwise

## `Job` {#job}

- `estimatedPrintTime`: The estimated print time for the file, in seconds.
- `lastPrintTime`: The print time of the last print of the file, in seconds.
- `filament`: Information regarding the estimated filament usage of the print job
- `filament.length`: Length of filament used, in mm
- `filament.volume`: Volume of filament used, in cm³

## `JobProgress` {#jobprogress}

- `completion`: Percentage of completion of the current print job
- `filepos`: Current position in the file being printed, in bytes from the beginning
- `printTime`: Time already spent printing, in seconds
- `printTimeLeft`: Estimate of time left to print, in seconds
- `printTimeLeftOrigin`: Origin of the current time left estimate. Can currently be either of:
    - `linear`: based on an linear approximation of the progress in file in bytes vs time
    - `analysis`: based on an analysis of the file
    - `estimate`: calculated estimate after stabilization of linear estimation
    - `average`: based on the average total from past prints of the same model against the same printer profile
    - `mixed-analysis`: mixture of estimate and analysis
    - `mixed-average`: mixture of estimate and average

## `Temperatures` {#temperatures}

An `Map` object. The `key` of the map is the name of the heater, such as "tool0", "bed". The `value` of the map is an [`Temperature`](#temperature) object.

## `Temperature` {#temperature}

- `actual`: Current temperature
- `target`: Target temperature, may be null if no target temperature is set.
- `offset`: Currently configured temperature offset to apply, will be left out for historic temperature information.

## `PrinterSettings` {#printersettings}

- `webcam_flipV`: `true` if the webcam is flipped vertically. Otherwise `false`.
- `webcam_flipH`: `true` if the webcam is flipped horizontally. Otherwise `false`.
- `webcam_streamRatio`: Webcam aspect ratio. Currently only	"4:3" and "16:9" are supported.
- `webcam_rotation`: `0` webcam rotation degree (clockwise). Possible values: [`0`, `90`, `180`, `270`].
- `agent_name`: The "agent" that connects to the server to represents the printer. Currently it can be either `octoprint_obico` or `moonraker_obico`.
- `agent_version`: The version of the agent.
- `temp_profiles`: An `List` of `Map` objects. The `key` of the map is the name of the heater, such as "chamber", "bed". The `value` of the map is the preset temperature.

## `TemperatureProfile` {#temperatureprofile}

- `actual`: Current temperature
- `target`: Target temperature, may be null if no target temperature is set.
- `offset`: Currently configured temperature offset to apply, will be left out for historic temperature information.

## `Print` {#print}

An object that represents a specific print job. If a G-Code file is printed multiple times, multiple print objects will be generated for each of them.

A dummy print object will be created when a timelapse video is uploaded to the server.

- `id`: ID used in API path. *ReadOnly*
- `printer`: ID of the [`Printer`](#printer) object.
- `filename`: G-Code filename for this print.
- `started_at`: The timestamp when the print starts. In ISO-8601 format.
- `finished_at`: The timestamp when the print finishes **successfully**. Null if the print is cancelled. In ISO-8601 format.
- `cancelled_at`: The timestamp when the print is cancelled. Null if the print finishes successfully. In ISO-8601 format.
- `uploaded_at`: The timestamp when the timelapse video is uploaded. Otherwise it'll be Null. In ISO-8601 format.
- `alerted_at`: The timestamp when a possible print failure is detected and alerted. Null if nothing is detected during the print. If multiple print failures are detected and alerted, only the last one is saved in this field. In ISO-8601 format.
- `alert_acknowledged_at`: The timestamp when the user comes to the app to respond to the failure alert. Null if the user never responds. If multiple print failures are detected and the user responds multiple times, only the last one is saved in this field. In ISO-8601 format.
- `alert_muted_at`: The timestamp when the user indicates the alert as a false, and tells the server to stop detection for the rest of the print. In ISO-8601 format.
- `paused_at`: The timestamp when the print is paused because of a detected print failure. If the print is paused (and resumed) multiple times before it ends, only the last one is saved in this field. In ISO-8601 format. Note: This field is not set if the user manually pauses the print.
- `video_url`: The URL for the timelapse video.
- `tagged_video_url`: The URL for the "tagged" timelapse video, i.e., the video with potential detected failures indicated in green boxes.
- `poster_url`: The URL for the "poster" of the video, i.e., the image a video player shows before the video starts playing.
- `prediction_json_url`: The URL for the json file of the detection result, frame by frame.
- `alert_overwrite`: The response the user gives about if a print failure has happened during the print. An `Enum`.
    - `FAILED`: There is(are) print failure(s).
    - `NOT_FAILED`: There are no print failures.
- `printshotfeedback_set`:

## `PrintShotFeedback` {#printshotfeedback}

An object that contains the info about a video frame (a snapshot) in a print timelapse video and the user input (feedback) to indicate if it contains any failure.

- `id`: ID used in API path. *ReadOnly*
- `print_id`: ID of the [`Print`](#print) object.
- `image_url`: The URL for the video frame.
- `answer`: The feedback provide by the user. An `Enum`.
    - `LOOKS_BAD`: It contains a failure.
    - `LOOKS_OK`: It doesn't contain any failure.
    - `UNANSWERED`: It can be determined if it contains a failure.
- `answered_at`: The timestamp when the user provides the feedback. Null if the user hasn't provided the feedback. In ISO-8601 format.

## `GCodeFile` {#gcodefile}

An object that represents a G-Code file.

- `id`: ID used in API path. *ReadOnly*
- `user`: The [`User`](#user) this GCodeFile belongs to.
- `filename`: The original filename uploaded.
- `safe_filename`: The filename that is safe for any file system.
- `url`: The URL from which the GCodeFile can be downloaded.
- `num_bytes`: The size of the GCodeFile in bytes.


## `User` {#user}

- `email`: Email.
- `consented_at`: The timestamp when the user has consented to the terms and conditions. It should always be the time when the user signs up. In ISO-8601 format.
- `dh_balance`: The balance of the AI Detection Hours.

## `PrinterEvent` {#printerevent}

An object that represents a printer-related event, detailing actions or states of a print job or printer.

- `id`: ID used in API path. ReadOnly
- `print`: The Print job associated with this event. Nullable
- `printer`: The Printer associated with this event.
- `event_type`: The type of event. Must be one of the predefined types:
    - `STARTED`: Print job started.
    - `ENDED`: Print job ended.
    - `PAUSED`: Print job paused.
    - `RESUMED`: Print job resumed.
    - `FAILURE_ALERTED`: Possible failure detected.
    - `ALERT_MUTED`: Alerts have been muted.
    - `ALERT_UNMUTED`: Alerts have been unmuted.
    - `FILAMENT_CHANGE`: Filament change required.
    - `PRINTER_ERROR`: Printer error occurred.
- `event_class`: The class of event, indicating severity or nature. Must be one of:
    - `ERROR`: Represents an error event.
    - `WARNING`: Represents a warning event.
    - `SUCCESS`: Represents a success event.
    - `INFO`: Represents an informational event.
- `event_title`: A title for the event. Auto-generated based on event_type if not provided. Nullable
- `event_text`: Detailed description of the event. Nullable
- `image_url`: URL to an image related to the event. Auto-generated if not provided. Nullable
- `info_url`: URL to additional information about the event. Nullable
- `created_at`: The timestamp when the event was created. ReadOnly