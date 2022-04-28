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
- Body: A [List] of [Printer](/docs/api/api-objects/#printer) objects.


## GET `/api/v1/printers/{:id}/`

### Request

#### Query parameters

None.

### Response

#### Success

- Code: `200`
- Body: A [Printer](/docs/api/api-objects/#printer) object.

#### Not found

When the printer specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## PATCH `/api/v1/printers/`

Partial update of the [Printer](/docs/api/api-objects/#printer) object.

### Request

#### Query parameters

None.

#### Body

JSON representation of the [Printer](/docs/api/api-objects/#printer) object, except the following read-only fields:


- `id`
- `created_at`
- `not_watching_reason`
- `pic`
- `status`: An [PrinterStatus](#printerstatus) object.
- `settings`: An [PrinterSettings](#printersettings) object.
- `current_print`: An [Print] object that represents the current print job of the printer. `Null` when the printer is idle.
- `normalized_p`: A normalized *prediction score* for failure detection. It's a number between 0 and 1. 0 means no failure is detected. 1 means the maximum confidence on predicting a print failure.
- `auth_token`: The token the printer can use to authenticate itself.
