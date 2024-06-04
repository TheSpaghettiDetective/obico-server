---
title: Snapshot Upload Api
---
## POST `/api/v1/octo/pic/` {#post-apiv1octopic}

### Request {#request}

#### Headers {#headers}
- `Authorization`: A required header with the authentication token for the printer.

#### Body {#body}

- `is_primary_camera`: A boolean. Indicates whether the image is from the primary camera. Defaults to true if not specified.
- `is_nozzle_camera`: A boolean. Indicates whether the image is from a nozzle camera. Defaults to false if not specified.
- `camera_name`: A string. The name of the camera.
- `pic`: A file. The image file to be uploaded.
- `viewing_boost`: A boolean (optional). Indicates whether the image is sent for viewing boost. Defaults to false if not specified.

### Response {#response}

#### Success {#success}

- Code: `200`
- Body: A JSON object with a success message.

  ```json
  {
    "result": "ok"
  }