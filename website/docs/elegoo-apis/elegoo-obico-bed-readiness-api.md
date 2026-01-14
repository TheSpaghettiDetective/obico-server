---
title: Elegoo-Obico Bed Readiness API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to detect bed readiness using Obico's AI-powered bed readiness detection system. This system uses advanced AI model to detect debris, tools, and wires on the print bed within a specified region of interest.


## Authentication {#authentication}

Authentication is performed using device credentials passed as form data parameters:

- `serial_no`: The device serial number registered in the system
- `access_token`: The access token associated with the device

These credentials must be included in the POST request along with other parameters.

:::tip
Use the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) to manage device credentials before using the bed readiness detection API.
:::

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/bed_readiness/` {#post-entpartnersapielegoobed-readiness}

### Request {#request}

This POST request should be sent as `multipart/form-data` format.

#### Form parameters {#form-parameters}

- `serial_no`: The device serial number. Required for authentication.
- `access_token`: The access token for the device. Required for authentication.
- `img`: Snapshot from the webcam for bed readiness detection. In JPEG format. Required.
- `bed_polygon`: JSON array of [x, y] coordinate pairs defining the bed region of interest. Must contain at least 3 points to form a valid polygon. Required.
- `sensitivity`: Integer between 1-10 (default: 5). Higher values make the detection more sensitive to smaller debris. Optional.
  - **1-3**: Low sensitivity - only detects large, obvious debris
  - **4-6**: Medium sensitivity (default: 5) - balanced detection
  - **7-10**: High sensitivity - detects small debris and fine particles

### Response {#response}

#### Status code: `200` {#status-code-200}

API request was processed successfully.

#### Body {#body}

```
{
  "score": 0.15,
  "message": "Okay"
}
```

- `score`: A float between 0.0 and 1.0 representing the bed readiness score.
  - `0.0`: The model is highly confident there are **NO** foreign objects on the print bed that could obstruct printing.
  - `1.0`: The model is highly confident there are foreign objects on the print bed that could obstruct printing.
  - Values between 0.0 and 1.0 represent level of confidence.
- `message`: A string indicating the status of the detection. Always `"Okay"` for successful detection.

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully due to validation errors or processing failures.

#### Body {#body-1}

```
{
  "score": null,
  "message": "Detailed error message"
}
```

Examples of error messages:
- `"Invalid JSON in bed_polygon parameter: {error details}"`
- `"Invalid parameter: bed_polygon must be a list of at least 3 points"`
- `"Invalid parameter: Each polygon point must be [x, y]"`
- `"Invalid parameter: sensitivity must be between 1 and 10"`
- `"Failed to process request: {error details}"`

#### Status code: `401` {#status-code-401}

Authentication failed. This can occur when:
- Missing `serial_no` or `access_token`
- Invalid credentials or expired access token

#### Body {#body-2}

```
{
  "error": "serial_no and access_token are required"
}
```

or

```
{
  "error": "Invalid credentials"
}
```

**Note:** Expired access tokens will also return the "Invalid credentials" error message.

#### Status code: `422` {#status-code-422}

API request was NOT processed successfully due to missing required parameters or semantic validation errors.

#### Body {#body-3}

**Missing required parameters:**
```
{
  "score": null,
  "message": "Error message"
}
```

Examples of error messages:
- `"Missing 'img' file parameter"`
- `"Missing 'bed_polygon' parameter"`

**Platform not found (semantic validation error):**
```
{
  "score": null,
  "message": "Print bed is not found in the expected position."
}
```

This error occurs when the `bed_polygon` coordinates do not match the actual print bed position in the image. This may indicate:
- Incorrect `bed_polygon` coordinates
- The print bed is not visible in the image
- The image does not contain the expected print bed area

:::tip
For most use cases, sensitivity level 5 provides the best balance between accuracy and false positive reduction. Higher sensitivity may detect very small particles that don't actually affect print quality.
:::

## Usage Example {#usage-example}

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/bed_readiness/ \
  -F "serial_no=ELEGOO_DEVICE_001" \
  -F "access_token=your_access_token_here" \
  -F "img=@/path/to/bed_snapshot.jpg" \
  -F "bed_polygon=[[100,100],[400,100],[400,300],[100,300]]" \
  -F "sensitivity=5"
```

### Bed Polygon Format
The `bed_polygon` parameter should be a JSON array of coordinate pairs defining the print bed area. For example:
- **Rectangular bed**: `[[x1,y1],[x2,y2],[x3,y3],[x4,y4]]`
- **Circular bed**: `[[center_x,center_y-radius],[center_x+radius,center_y],[center_x,center_y+radius],[center_x-radius,center_y]]`

:::warning
Passing the wrong `bed_polygon` will result in unpredictable result.
:::

:::tip
Make sure to register your device credentials using the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) before calling the bed readiness detection API.
:::