---
title: Elegoo-Obico Plate Analysis API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to analyze 3D printing plates using Obico's AI-powered plate analysis system. This system uses advanced AI models to analyze 3D models based on isometric images and provide detailed model analysis along with recommended printing strategies.


## Authentication {#authentication}

Authentication is performed using user credentials passed as request parameters:

- `elegoo_user_id`: The Elegoo user identifier registered in the system
- `access_token`: The access token associated with the user

These credentials can be included either in the POST request body (JSON) or as query parameters.

:::tip
Use the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) to manage user credentials before using the plate analysis API.
:::

## Language Support {#language-support}

API responses can be returned in different languages using the `lang` query parameter. See the [Elegoo-Obico Language Support](./elegoo-obico-language-support.md) documentation for details on supported languages and usage.

**Example:**
```bash
POST /ent/partners/api/elegoo/plate_analysis/?lang=zh-CN
```

:::note
The `language` body parameter (documented below) is deprecated. Please use the `lang` query parameter instead.
:::

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/plate_analysis/` {#post-entpartnersapielegooplate-analysis}

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `elegoo_user_id`: The Elegoo user identifier. Required for authentication. Can also be passed as query parameter.
- `access_token`: The access token for the user. Required for authentication. Can also be passed as query parameter.
- `language`: **Deprecated.** The language for the response. Optional. Defaults to `"English"`. Use the `lang` query parameter instead (see [Language Support](#language-support) section above).
- `messages`: Array of chat messages. Optional. Used for context tracking.
- `chat_id`: Session identifier for the chat. Optional. Used for context tracking.
- `images`: Array of base64-encoded image strings. Required. Isometric images of the 3D model to analyze.
- `plates`: Array of plate objects. Required. Each plate object should contain:
  - `model_objects`: Array of model objects on the plate. At least one model object is required.
    - `extruder_id`: Integer. The extruder ID for the model.
    - `id`: String. Unique identifier for the model.
    - `name`: String. Name of the model file.

#### Example request {#example-request}

```json
{
  "elegoo_user_id": "ELEGOO_USER_001",
  "access_token": "your_access_token_here",
  "chat_id": "chat_session_123",
  "messages": [],
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  ],
  "plates": [
    {
      "model_objects": [
        {
          "extruder_id": 1,
          "id": "52",
          "name": "Octopus_Head_v6.stl"
        }
      ]
    }
  ]
}
```

### Response {#response}

#### Status code: `201` {#status-code-201}

API request was processed successfully.

#### Body {#body}

```json
{
  "message": {
    "role": "assistant",
    "content": "This appears to be an **octopus head model** with intricate tentacle details. The design features multiple overhangs that will require support structures. Based on the geometry, I recommend using tree supports for the tentacles. Would you like me to proceed with this printing strategy?",
    "suggested_printing_method": "Use tree supports for the tentacle overhangs. Add a brim to improve bed adhesion. Ensure adequate cooling for the fine details."
  },
  "credit_resp": {
    "code": 0,
    "data": null,
    "msg": "",
    "traceId": "00000000000000000000000000000000"
  }
}
```

- `message`: An object containing the assistant's response.
  - `role`: Always `"assistant"`.
  - `content`: A conversational analysis of the 3D model (less than 500 characters) that includes:
    - Model identification and description
    - Intended use analysis
    - Geometric features and printability considerations
    - Uses **bold text** for key features
    - Ends with a question inviting user confirmation
  - `suggested_printing_method`: A recommended printing strategy focusing on technical aspects such as support type (normal or tree), brim/raft recommendations, and overall approach. Does not include specific slicer settings or orientation.
- `credit_resp`: Object or null. The response from the Elegoo credits API. Contains the result of the credit deduction operation.
  - `code`: Integer. `0` indicates success.
  - `data`: Object or null. Additional data from the credits API.
  - `msg`: String. Message from the credits API.
  - `traceId`: String. Trace identifier for debugging.

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully due to validation errors or processing failures.

#### Body {#body-1}

```json
{
  "message": {
    "role": "assistant",
    "content": "Error message"
  }
}
```

Examples of error messages:
- `"No plates are found in the project. Please contact support."`
- `"Oops, you need to add at least one model."`
- `"No images found for analysis. Please contact support."`

#### Status code: `401` {#status-code-401}

Authentication failed. This can occur when:
- Missing `elegoo_user_id` or `access_token`
- Invalid credentials or expired access token

#### Body {#body-2}

```json
{
  "error": "elegoo_user_id and access_token are required"
}
```

or

```json
{
  "error": "Invalid or expired access token"
}
```

**Note:** Expired access tokens will return the "Invalid or expired access token" error message.

#### Status code: `402` {#status-code-402}

Insufficient Elegoo credits. The user does not have enough credits to perform the requested operation. This status code is returned when the Elegoo credits API responds successfully but indicates insufficient credits.

#### Body {#body-3}

```json
{
  "code": 402,
  "error": "Error in calling Elegoo credits API",
  "credit_resp": {
    "code": 10012,
    "data": null,
    "msg": "user not exist",
    "traceId": "00000000000000000000000000000000"
  }
}
```

- `code`: Integer. Always `402`.
- `error`: String. Generic error message indicating a credit API error.
- `credit_resp`: Object. The response from the Elegoo credits API containing detailed error information.
  - `code`: Integer. Error code from the credits API (e.g., `10012` for user not found, `402` for insufficient credits).
  - `data`: Object or null. Additional data from the credits API.
  - `msg`: String. Detailed error message from the credits API.
  - `traceId`: String. Trace identifier for debugging.

#### Status code: `502` {#status-code-502}

Elegoo credits API failure. This status code is returned when the Elegoo credits API fails to respond properly due to connection issues, server errors, or other API failures.

#### Body {#body-4}

The response body varies depending on the type of failure:

**Connection error or timeout:**
```json
{
  "code": 502,
  "error": "Elegoo API connection error or timeout"
}
```

**Server error (5xx):**
```json
{
  "code": 502,
  "error": "Elegoo API server returns 5XX"
}
```

**Unexpected HTTP error (4xx):**
```json
{
  "code": 502,
  "error": "Elegoo API returns unexpected HTTP error"
}
```

**JSON parsing failure or other request errors:**
```json
{
  "code": 502,
  "error": "Error in calling Elegoo credits API"
}
```

or

```json
{
  "code": 502,
  "error": "Elegoo API request failed"
}
```

- `code`: Integer. Always `502`.
- `error`: String. Specific error message indicating the type of API failure.
- `credit_resp`: Not included in 502 responses (will be `null` if accessed).

## Usage Example {#usage-example}

```bash
curl -X POST "https://elegoo-app.obico.io/ent/partners/api/elegoo/plate_analysis/?lang=zh-CN" \
  -H "Content-Type: application/json" \
  -d '{
    "elegoo_user_id": "ELEGOO_USER_001",
    "access_token": "your_access_token_here",
    "chat_id": "chat_session_123",
    "images": ["data:image/jpeg;base64,/9j/4AAQSkZJRg..."],
    "plates": [{
      "model_objects": [{
        "extruder_id": 1,
        "id": "52",
        "name": "Octopus_Head_v6.stl"
      }]
    }]
  }'
```

### Image Format {#image-format}

The `images` parameter should be an array of base64-encoded image strings. Images should be isometric views of the 3D model positioned on the print bed (indicated by grid lines). Multiple images can be provided for more comprehensive analysis.

:::tip
Make sure to register your user credentials using the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) before calling the plate analysis API.
:::

:::warning
The model must already be positioned on the print bed in the images. The analysis assumes the model is ready for slicing and focuses on printing strategy rather than orientation.
:::



