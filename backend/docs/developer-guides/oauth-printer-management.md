# OAuth Printer Management API

This guide describes how third-party applications can use OAuth to manage printers and prints without requiring the Obico Agent.

## Overview

The OAuth Printer Management API allows applications to:
- Create and manage printers
- Start and finish print sessions
- Submit images for AI failure detection

This is useful for:
- Custom printer firmware integrations
- Third-party mobile apps
- Automated print farm management systems

## Authentication

All endpoints require OAuth2 Bearer token authentication.

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://your-obico-server/api/v1/printers/
```

### Getting an Access Token

```bash
curl -X POST https://your-obico-server/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

Response:
```json
{
  "access_token": "abc123...",
  "expires_in": 3153600000,
  "token_type": "Bearer",
  "scope": "read write"
}
```

## API Endpoints

### Create Printer

Create a new printer for the authenticated user.

**Endpoint:** `POST /api/v1/printers/`

**Request Body:**
```json
{
  "name": "My 3D Printer"
}
```

**Response:** `201 Created`
```json
{
  "id": 123,
  "name": "My 3D Printer",
  "auth_token": "a1b2c3d4e5f6...",
  "created_at": "2024-01-15T10:30:00Z",
  "current_print": null,
  ...
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My 3D Printer"}' \
  https://your-obico-server/api/v1/printers/
```

---

### List Printers

Get all printers for the authenticated user.

**Endpoint:** `GET /api/v1/printers/`

**Response:** `200 OK`
```json
[
  {
    "id": 123,
    "name": "My 3D Printer",
    "current_print": null,
    ...
  }
]
```

---

### Get Printer

Get details of a specific printer.

**Endpoint:** `GET /api/v1/printers/{id}/`

**Response:** `200 OK`
```json
{
  "id": 123,
  "name": "My 3D Printer",
  "current_print": {
    "id": 456,
    "filename": "benchy.gcode",
    "started_at": "2024-01-15T10:30:00Z"
  },
  ...
}
```

---

### Start Print

Start a new print session. If a print is already in progress, it will be automatically finished before starting the new one.

**Endpoint:** `POST /api/v1/printers/{id}/start_print/`

**Request Body:**
```json
{
  "filename": "benchy.gcode"
}
```

**Response:** `200 OK`
```json
{
  "succeeded": true,
  "printer": {
    "id": 123,
    "current_print": {
      "id": 456,
      "filename": "benchy.gcode",
      "started_at": "2024-01-15T10:30:00Z"
    },
    ...
  }
}
```

**Errors:**
- `400 Bad Request` - Missing required `filename` field

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "benchy.gcode"}' \
  https://your-obico-server/api/v1/printers/123/start_print/
```

---

### Finish Print

End the current print session.

**Endpoint:** `POST /api/v1/printers/{id}/finish_print/`

**Request Body:**
```json
{
  "status": "success"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Either `"success"` (default) or `"cancelled"` |

**Response:** `200 OK`
```json
{
  "succeeded": true,
  "printer": {
    "id": 123,
    "current_print": null,
    ...
  }
}
```

**Errors:**
- `404 Not Found` - Printer is not currently printing

**Example (successful print):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "success"}' \
  https://your-obico-server/api/v1/printers/123/finish_print/
```

**Example (cancelled print):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}' \
  https://your-obico-server/api/v1/printers/123/finish_print/
```

---

### Predict (AI Failure Detection)

Submit an image for AI-based failure detection analysis.

**Endpoint:** `POST /api/v1/printers/{id}/predict/`

**Request:** `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| img | file | Yes | JPEG image of the print bed |

**Response:** `200 OK`
```json
{
  "result": {
    "p": 0.0234,
    "detections": [
      {
        "confidence": 0.85,
        "bbox": [100, 150, 200, 250]
      }
    ]
  },
  "temporal_stats": {
    "ewm_mean": 0.0312,
    "rolling_mean_short": 0.0289,
    "rolling_mean_long": 0.0245
  },
  "normalized_p": 0.0156
}
```

| Field | Description |
|-------|-------------|
| `result.p` | Raw prediction probability (0-1) |
| `result.detections` | Array of detected failure regions |
| `temporal_stats.ewm_mean` | Exponentially weighted moving average |
| `temporal_stats.rolling_mean_short` | Short-term rolling average |
| `temporal_stats.rolling_mean_long` | Long-term rolling average |
| `normalized_p` | Final normalized probability after temporal smoothing |

**Errors:**
- `400 Bad Request` - Missing `img` field
- `404 Not Found` - Printer is not currently printing

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "img=@/path/to/print_image.jpg" \
  https://your-obico-server/api/v1/printers/123/predict/
```

---

## Typical Workflow

1. **Create a printer** (one-time setup):
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Printer"}' \
     https://your-obico-server/api/v1/printers/
   ```

2. **Start a print** when printing begins:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"filename": "model.gcode"}' \
     https://your-obico-server/api/v1/printers/123/start_print/
   ```

3. **Submit images periodically** for failure detection:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -F "img=@snapshot.jpg" \
     https://your-obico-server/api/v1/printers/123/predict/
   ```

4. **Finish the print** when done:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "success"}' \
     https://your-obico-server/api/v1/printers/123/finish_print/
   ```

## Error Handling

All endpoints return standard HTTP status codes:

| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created (for POST /printers/) |
| 400 | Bad Request (missing/invalid parameters) |
| 401 | Unauthorized (invalid or missing token) |
| 403 | Forbidden (token valid but no access to resource) |
| 404 | Not Found (printer doesn't exist or not printing) |

Error responses include a detail message:
```json
{
  "detail": "Printer is not currently printing."
}
```

Or for validation errors:
```json
{
  "filename": ["This field is required."]
}
```
