---
title: Printer Event API
---

## POST `/api/v1/printer_events/` {#post-apiv1printerevents}

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

## GET `/api/v1/printer_events/` {#get-apiv1printerevents}

### Request {#request}

#### Headers {#headers}

- `Authorization`: A required header with the authentication token for the printer.

#### Query parameters {#query-parameters}

- `filter_by_classes`: (optional): An array of strings representing classes to filter the events by.
- `filter_by_types[]`: (optional): An array of strings representing types to filter the events by.
- `start`: (optional): An integer representing the start index for pagination (default is 0).
- `limit`: An integer representing the maximum number of results to return per page (default is 12).

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A JSON array containing serialized [PrinterEvent] objects.