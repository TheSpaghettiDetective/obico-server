---
title: G-Code file API
---

## GET `/api/v1/g_code_files/` {#get-apiv1gcodes}

### Request {#request}

#### Query parameters {#query-parameters}

- `page`: Which page of objects to return. For pagination.
- `page_size`: The number of objects to return. For pagination.

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A `List` of [`GCodeFile`](/docs/api/api-objects/#gcodefile) objects.


## GET `/api/v1/g_code_files/{:id}/` {#get-apiv1gcodesid}

### Request {#request-1}

#### Query parameters {#query-parameters-1}

None.

### Response {#response-1}

#### Success {#success-1}

- Code: `200`
- Body: A [`GCodeFile`](/docs/api/api-objects/#gcodefile) objects.

#### Not found {#not-found}

When the G-Code file specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## DELETE `/api/v1/g_code_files/{:id}/` {#delete-apiv1gcodesid}

Delete the [`GCodeFile`](/docs/api/api-objects/#gcodefile) object specified by `{:id}`

### Response {#response-2}

#### Success {#success-2}

- Code: `200`
- Body: Empty.

#### Not found {#not-found-1}

When the G-Code file specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`
