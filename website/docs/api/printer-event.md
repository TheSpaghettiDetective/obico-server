---
title: Printer Event API
---

## POST `/api/v1/octo/printer_events/` {#post-apiv1octoprinterevents}

### Request {#request}

#### Headers {#headers}

- `Authorization`: A required header with the authentication token for the printer.

#### Body {#body}
JSON representation of the [`PrinterEvent`] object.
- `event_type`: A `string`. The type of the event.
- `event_class`: A `string`. The class of the event.
- `event_title`: A `string`. The title of the event.
- `event_text`: A `string`. The detailed text of the event.
- `info_url`: A `string` (optional). URL for more information related to the event.
- `notify`: A `boolean` (optional). If set to `true`, a notification task will be created.
- `snapshot`: A `file` (optional). An image file related to the event.

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A JSON object with a success message.

  ```json
  {
    "result": "ok"
  }

## GET `/api/v1/octo/printer_events/` {#get-apiv1printerevents}

### Request {#request}

#### Headers {#headers}

- `Authorization`: A required header with the authentication token for the printer.

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A JSON array containing serialized [PrinterEvent] objects.