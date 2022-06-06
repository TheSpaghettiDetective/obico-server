---
title: G-Code file API
---

## GET `/api/v1/gcodes/`

### Request

#### Query parameters

- `page`: Which page of objects to return. For pagination.
- `page_size`: The number of objects to return. For pagination.

### Response

#### Success

- Code: `200`
- Body: A `List` of [`GCodeFile`](/docs/api/api-objects/#gcodefile) objects.


## GET `/api/v1/gcodes/{:id}/`

### Request

#### Query parameters

None.

### Response

#### Success

- Code: `200`
- Body: A [`GCodeFile`](/docs/api/api-objects/#gcodefile) objects.

#### Not found

When the G-Code file specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## DELETE `/api/v1/gcodes/{:id}/`

Delete the [`GCodeFile`](/docs/api/api-objects/#gcodefile) object specified by `{:id}`

### Response

#### Success

- Code: `200`
- Body: Empty.

#### Not found

When the G-Code file specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`
