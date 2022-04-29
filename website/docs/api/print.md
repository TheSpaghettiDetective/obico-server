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

- `id`
- `printer`
- `filename`
- `started_at`
- `finished_at`
- `cancelled_at`
- `uploaded_at`
- `alerted_at`
- `alert_acknowledged_at`
- `alert_muted_at`
- `paused_at`
- `video_url`
- `tagged_video_url`
- `poster_url`
- `prediction_json_url`

### Response

#### Success

- Code: `200`
- Body: A [`Print`](/docs/api/api-objects/#print) object.

#### Not found

When the print specified by the `{:id}` doesn't exist, or the access is not authorized by the authenticated user.

- Code: `404`
