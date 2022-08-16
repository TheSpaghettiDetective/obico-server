---
title: Printer API
---

## GET `/api/v1/printers/` {#get-apiv1printers}

### Request {#request}

#### Query parameters {#query-parameters}

- `with_archived`: Boolean. Default to `false`. Whether or not archived printer need to be returned.

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A `List` of [`Printer`](/docs/api/api-objects/#printer) objects.


## GET `/api/v1/printers/{:id}/` {#get-apiv1printersid}

### Request {#request-1}

#### Query parameters {#query-parameters-1}

None.

### Response {#response-1}

#### Success {#success-1}

- Code: `200`
- Body: A [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## PATCH `/api/v1/printers/{:id}/` {#patch-apiv1printersid}

Partial update of the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-2}

#### Query parameters {#query-parameters-2}

None.

#### Body {#body}

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

### Response {#response-2}

#### Success {#success-2}

- Code: `200`
- Body: A [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-1}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## DELETE `/api/v1/printers/{:id}/` {#delete-apiv1printersid}

Delete the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Response {#response-3}

#### Success {#success-3}

- Code: `200`
- Body: Empty.

#### Not found {#not-found-2}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/cancel_print` {#post-apiv1printersidcancel_print}

Cancel the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-3}

None.

### Response {#response-4}

#### Success {#success-4}

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the cancel command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-3}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/pause_print` {#post-apiv1printersidpause_print}

Pause the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-4}

None.

### Response {#response-5}

#### Success {#success-5}

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the pause command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-4}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/resume_print` {#post-apiv1printersidresume_print}

Resume the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-5}

None.

### Response {#response-6}

#### Success {#success-6}

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the resume command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-5}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/mute_current_print` {#post-apiv1printersidmute_current_print}

Mute (temporarily disable failure detection for the rest of the print) the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-6}

None.

### Response {#response-7}

#### Success {#success-7}

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the mute command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-6}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## POST `/api/v1/printers/{:id}/acknowledge_alert` {#post-apiv1printersidacknowledge_alert}

Acknowledge an failure alert for the current print on the [`Printer`](/docs/api/api-objects/#printer) object specified by `{:id}`

### Request {#request-7}

None.

### Response {#response-8}

#### Success {#success-8}

- Code: `200`
- Body: An `Object`
    - `succeeded`. `true` if the acknowledge command was successfully sent to the printer. Please note this doesn't mean the cancel command is successfully executed in the client. `false` if the command failed for any reason, such as the printer is not currently printing.
    - `printer` The updated [`Printer`](/docs/api/api-objects/#printer) object.

#### Not found {#not-found-7}

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`