---
title: Print API
---

## GET `/api/v1/prints/`

### Request

#### Query parameters

- `filter`: An `Enum`.
    - `cancelled`: Return only the prints that are cancelled.
    - `finished`: Return only the prints that finish **successfully**.
    - `need_alert_overwrite`: Return only the prints with `alert_overwrite == null`.
    - `need_print_shot_feedback`: Return only the prints that has associated ['PrintShotFeedback`](/docs/api/api-objects/#printshotfeedback) objects but none of them has `answer` set.
- `sorting`: An `Enum`.
    - `date_desc`: The returned `Print` objects are sorted by *start time* in descending order.
    - `date_asc`: The returned `Print` objects are sorted by *start time* in ascending order.
- `start`: The number of objects at the beginning of the result to skip. Not valid if `sorting` is absent. For pagination.
- `limit`: The number of objects to return. Not valid if `sorting` is absent. For pagination.

### Response

#### Success

- Code: `200`
- Body: A `List` of [`Print`](/docs/api/api-objects/#print) objects.


## GET `/api/v1/print/{:id}/`

### Request

#### Query parameters

None.

### Response

#### Success

- Code: `200`
- Body: A [`Printer`](/docs/api/api-objects/#print) object.

#### Not found

When the print specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## PATCH `/api/v1/prints/{:id}/`

Partial update of the [`Print`](/docs/api/api-objects/#print) object specified by `{:id}`

### Request

#### Query parameters

None.

#### Body

JSON representation of the [`Print`](/docs/api/api-objects/#print) object, except the following read-only fields:

- `id`.
- `printer`. Always the printer on which it's printed on (duh!).
- `filename`. Maybe an argument can be made that the G-Code file name can be changed once the print has started. But we haven't seen this case in the real world yet.
- `started_at`. Always the timestamp when the print starts.
- `finished_at`. Always the timestamp when the print finishes **successfully**.
- `cancelled_at`. Always the timestamp when the print is cancelled.
- `uploaded_at`. Always the timestamp when the time-lapse video is uploaded.
- `alerted_at`. Check the [Websocket](/docs/api/websocket/) for how this field is set.
- `alert_acknowledged_at`. Automatically set based on the rules. Check [`Print`](/docs/api/api-objects/#print) for details.
- `alert_muted_at`. Automatically set based on the rules. Check [`Print`](/docs/api/api-objects/#print) for details.
- `paused_at`. Automatically set based on the rules. Check [`Print`](/docs/api/api-objects/#print) for details.
- `video_url`. Automatically generated when a time-lapse is generated and saved to the storage.
- `tagged_video_url`. Automatically generated when a time-lapse is generated and saved to the storage.
- `poster_url`. Automatically generated when a time-lapse is generated and saved to the storage.
- `prediction_json_url`. Automatically generated when a time-lapse is generated and saved to the storage.

### Response

#### Success

- Code: `200`
- Body: A [`Print`](/docs/api/api-objects/#print) object.

#### Not found

When the print specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`


## DELETE `/api/v1/prints/{:id}/`

Delete the [`Print`](/docs/api/api-objects/#print) object specified by `{:id}`

### Response

#### Success

- Code: `200`
- Body: Empty.

#### Not found

When the print specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`



## GET `/api/v1/prints/{:id}/prediction_json`

Retrieve the prediction (failure detection) json associated with the [`Print`](/docs/api/api-objects/#print) specified by `{:id}`

### Response

#### Success

- Code: `200`
- Body: A JSON that represents the frame-by-frame predictions.

#### Not found

When the print specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`