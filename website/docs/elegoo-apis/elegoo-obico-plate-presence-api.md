---
title: Elegoo-Obico Plate Presence API
unlisted: true
---

The API documented on this page is designed for Elegoo partners to detect a missing build plate before a print starts. Ring markers are printed on the printer's magnetic pad. When the build plate is installed, it covers them. When one of these markers is visible in the camera photo, the build plate is missing.

The detection uses classical image processing, not an AI model. It needs to know where each marker appears in this printer's camera photo, so the device sends its own marker measurements with every request. See [Measuring the markers](#measuring-the-markers).

## Authentication {#authentication}

Authentication is performed using device credentials passed as form data parameters:

- `serial_no`: The device serial number registered in the system
- `access_token`: The access token associated with the device

These credentials must be included in the POST request along with other parameters.

:::tip
Use the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) to manage device credentials before using the plate presence API.
:::

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/plate_presence/` {#post-entpartnersapielegooplate-presence}

### Request {#request}

This POST request should be sent as `multipart/form-data` format.

#### Form parameters {#form-parameters}

- `serial_no`: The device serial number. Required for authentication.
- `access_token`: The access token for the device. Required for authentication.
- `img`: Snapshot from the chamber camera, taken at the bed height the printer uses for this check. In JPEG format, at the same resolution the markers were measured on. Required.
- `markers`: JSON array of this unit's marker measurements, one entry per marker. Required. Each entry has exactly these fields:
  - `position`: Which marker this is. One of `"front"`, `"left"`, `"back"`, `"right"`. Each position may appear at most once.
  - `x`, `y`: The marker's center in the photo, in pixels. `(0, 0)` is the top-left corner of the photo.
  - `w`, `h`: The width and height, in pixels, of the marker's outer ink ring as it appears in the photo. The markers look like flattened ellipses because the camera sees the pad at an angle, so `h` is usually much smaller than `w`.
  - `design`: The code of the ring artwork printed at this position. See [Design codes](#design-codes).
- `tolerance`: How far, in pixels, a detected marker's center may be from the measured `x`, `y`, measured as a straight line. Optional. Default `50`. Must be greater than 0 and at most `100`. A larger value tolerates less accurate measurements but makes each request slower.

Example `markers` value, measured on a DVT2 unit in November 2026:

```json
[
  {"position": "front", "x": 590, "y": 660, "w": 112, "h": 50, "design": "E"},
  {"position": "left",  "x": 282, "y": 484, "w": 61,  "h": 17, "design": "F"},
  {"position": "back",  "x": 624, "y": 420, "w": 51,  "h": 11, "design": "E"},
  {"position": "right", "x": 956, "y": 491, "w": 64,  "h": 20, "design": "F"}
]
```

### Response {#response}

#### Status code: `200` {#status-code-200}

API request was processed successfully.

#### Body {#body}

```
{
  "plate_missing": true,
  "markers_found": [
    {"position": "front", "x": 591.0, "y": 662.0, "w": 110.4, "h": 49.2}
  ]
}
```

- `plate_missing`: `true` when at least one marker was found within `tolerance` of where it was measured. The build plate is missing.
  - `false` means no marker was found. This is **not** proof that the build plate is installed: a marker can also go unseen because of glare, dirt on the marker, a moved camera, or outdated measurements.
- `markers_found`: The markers that were found, with the center (`x`, `y`) and size (`w`, `h`) where they were detected in this photo. Empty when `plate_missing` is `false`.

#### Status code: `400` {#status-code-400}

API request was NOT processed because a parameter is missing or invalid. Nothing is guessed: an invalid measurement is always rejected, never adjusted.

#### Body {#body-1}

```
{
  "error": "Detailed error message"
}
```

Examples of error messages:
- `"img is required"`
- `"img is not a readable image"`
- `"markers is required"`
- `"markers must be a non-empty JSON array"`
- `"markers[0] must have exactly the fields ['design', 'h', 'position', 'w', 'x', 'y']"`
- `"markers[1].position \"front\" appears more than once"`
- `"markers[2].design must be one of ['E', 'F']"`
- `"markers[0].w and h must be greater than 0"`
- `"markers[3] center (1300, 491) is outside the 1280x720 image"`
- `"tolerance must be greater than 0 and at most 100"`

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

#### Status code: `500` {#status-code-500}

The detection service was temporarily unavailable. The request can be retried.

## Measuring the markers {#measuring-the-markers}

Measure each unit's markers on that unit's own camera photo, taken with the build plate removed, before the printer goes live.

- **Bed height:** Take the measurement photo at the same bed height the printer uses for the plate presence check. The markers' position and shape in the photo change with bed height.
- **Resolution:** Measure on a photo at the same resolution the printer sends to this API. The coordinates are in pixels of that photo.
- **Center (`x`, `y`):** The center of the marker's outer ink ring.
- **Size (`w`, `h`):** The full width and height of the outer ink ring, edge to edge, as it appears in the photo. Measure the size as accurately as you can, within about 5%. In our tests, a size off by 10% already made the marker go unseen in up to 1 photo in 5, and a size 25% too small in about 1 photo in 3.
- **Accuracy:** The detected center must be within `tolerance` pixels (default 50) of the measured center. Accurate centers still work best: in our tests with the plate removed, exactly measured centers found a marker in 116 of 117 photos, and centers off by up to 50 pixels in 110 of 117.

Measure again whenever the measurements may no longer match the photo:
- the camera is moved, replaced or re-mounted,
- the bed height used for the check changes,
- the magnetic pad is replaced.

Outdated measurements do not cause an error. Instead, markers stop being found, and a missing plate goes unwarned. We recommend a re-measurement step in the service flow for these repairs.

:::tip
Detection relies mostly on the marker nearest the camera (`front`). Keep its print clean and high-contrast.
:::

### Design codes {#design-codes}

Each marker is a bright ink disc, a dark ring around it, and a bright outer ink ring. The design code says which proportions are printed:

- `E`: wide ink disc, dark ring, outer ink ring. Used at the `front` and `back` positions on the November 2026 DVT2 pad.
- `F`: small ink disc, dark ring, wide outer ink ring. Used at the `left` and `right` positions on the November 2026 DVT2 pad.

If the pad artwork changes, these codes change too. Please contact the Obico team before shipping new artwork, so a matching design code can be added.

## Usage Example {#usage-example}

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/plate_presence/ \
  -F "serial_no=ELEGOO_DEVICE_001" \
  -F "access_token=your_access_token_here" \
  -F "img=@/path/to/chamber_snapshot.jpg" \
  -F 'markers=[{"position":"front","x":590,"y":660,"w":112,"h":50,"design":"E"},{"position":"right","x":956,"y":491,"w":64,"h":20,"design":"F"}]' \
  -F "tolerance=50"
```

:::tip
Make sure to register your device credentials using the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) before calling the plate presence API.
:::
