---
title: Printer API
---

## GET `/api/v1/printers/`

### Request

#### Query parameters

- `with_archived`: Boolean. Default to `false`. Whether or not archived printer need to be returned.

### Response

#### Success

- Code: `200`
- Body: A `List` of [`Printer`](/docs/api/api-objects/#printer) objects.


## GET `/api/v1/printers/{:id}/`

### Request

#### Query parameters

None.

### Response

#### Success

- Code: `200`
- Body: A [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## PATCH `/api/v1/printers/{:id}/`

Partial update of the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

#### Query parameters

None.

#### Body

JSON representation of the [`Printer`](/docs/api/api-objects/#printer) object, except the following read-only fields:


- `id`.
- `created_at`. Always the timestamp when the printer is created.
- `not_watching_reason`. Automatically derived based on the watching rules.
- `pic`. Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `status`. Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `settings`. Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `current_print`.  Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `normalized_p`.   Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `auth_token`. System-generated.

### Response

#### Success

- Code: `200`
- Body: A [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## DELETE `/api/v1/printers/{:id}/`

Delete the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Response

#### Success

- Code: `200`
- Body: Empty.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/cancel_print`

Cancel the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

None.

### Response

#### Success

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the cancel command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/pause_print`

Pause the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

None.

### Response

#### Success

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the pause command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/resume_print`

Resume the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

None.

### Response

#### Success

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the resume command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/mute_current_print`

Mute (temporarily disable failure detection for the rest of the print) the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

None.

### Response

#### Success

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the mute command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/acknowledge_alert`

Acknowledge an failure alert for the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request

None.

### Response

#### Success

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the acknowledge command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`