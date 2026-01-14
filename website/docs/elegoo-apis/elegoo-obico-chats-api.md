---
title: Elegoo-Obico Chats API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to manage chat sessions with Obico's AI-powered chat assistant for 3D printing slicer guidance. This API allows you to create new chat sessions and retrieve existing chat sessions.


## Authentication {#authentication}

Authentication is performed using user credentials passed as request parameters:

- `elegoo_user_id`: The Elegoo user identifier registered in the system
- `access_token`: The access token associated with the user

These credentials can be included either in the POST request body (JSON), GET request query parameters, or as query parameters for POST requests.

:::tip
Use the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) to manage user credentials before using the chats API.
:::

## Language Support {#language-support}

API responses can be returned in different languages using the `lang` query parameter. See the [Elegoo-Obico Language Support](./elegoo-obico-language-support.md) documentation for details on supported languages and usage.

**Example:**
```bash
GET /ent/partners/api/elegoo/chats/?lang=zh-CN
```

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## GET `/ent/partners/api/elegoo/chats/` {#get-entpartnersapielegoochats}

Retrieves a list of all chat sessions for the authenticated user, ordered by most recent first.

### Request {#request}

#### Query parameters {#query-parameters}

- `elegoo_user_id`: The Elegoo user identifier. Required for authentication.
- `access_token`: The access token for the user. Required for authentication.

#### Example request {#example-request}

```bash
GET /ent/partners/api/elegoo/chats/?elegoo_user_id=ELEGOO_USER_001&access_token=your_access_token_here
```

### Response {#response}

#### Status code: `200` {#status-code-200}

API request was processed successfully.

#### Body {#body}

```json
[
  {
    "id": 1,
    "messages": "[{\"role\":\"user\",\"content\":\"What settings should I use?\"},{\"role\":\"assistant\",\"content\":\"I can help you with that...\"}]",
    "machine_name": "Elegoo Neptune 4",
    "filament_name": "PLA Generic",
    "print_process_name": "0.20mm Standard",
    "slicing_settings_json": "{\"temperature\":[\"220\"]}",
    "user_feedback": null,
    "user_feedback_text": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": 2,
    "messages": "[{\"role\":\"user\",\"content\":\"How do I fix layer shifting?\"}]",
    "machine_name": null,
    "filament_name": null,
    "print_process_name": null,
    "slicing_settings_json": null,
    "user_feedback": "positive",
    "user_feedback_text": "Very helpful!",
    "created_at": "2024-01-14T14:20:00Z",
    "updated_at": "2024-01-14T14:25:00Z"
  }
]
```

- Array of chat objects, each containing:
  - `id`: Integer. Unique identifier for the chat session.
  - `messages`: String. JSON-encoded array of chat messages representing the conversation history.
  - `machine_name`: String. Optional. Name of the printer/machine associated with this chat.
  - `filament_name`: String. Optional. Name of the filament preset associated with this chat.
  - `print_process_name`: String. Optional. Name of the print process preset associated with this chat.
  - `slicing_settings_json`: String. Optional. JSON-encoded object containing slicing configuration information.
  - `user_feedback`: String. Optional. User feedback value (e.g., "positive", "negative"). Maximum length 16 characters.
  - `user_feedback_text`: String. Optional. Additional text feedback from the user.
  - `created_at`: String. ISO 8601 timestamp indicating when the chat was created.
  - `updated_at`: String. ISO 8601 timestamp indicating when the chat was last updated.

#### Status code: `401` {#status-code-401}

Authentication failed. This can occur when:
- Missing `elegoo_user_id` or `access_token`
- Invalid credentials or expired access token

#### Body {#body-1}

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

## POST `/ent/partners/api/elegoo/chats/` {#post-entpartnersapielegoochats}

Creates a new chat session for the authenticated user.

### Request {#request-1}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `elegoo_user_id`: The Elegoo user identifier. Required for authentication. Can also be passed as query parameter.
- `access_token`: The access token for the user. Required for authentication. Can also be passed as query parameter.
- `messages`: String. Required. JSON-encoded array of chat messages representing the conversation history.
  - Each message object should have:
    - `role`: String. Either `"user"` or `"assistant"`.
    - `content`: String. The message content.
- `machine_name`: String. Optional. Name of the printer/machine associated with this chat.
- `filament_name`: String. Optional. Name of the filament preset associated with this chat.
- `print_process_name`: String. Optional. Name of the print process preset associated with this chat.
- `slicing_settings_json`: String. Optional. JSON-encoded object containing slicing configuration information.
- `user_feedback`: String. Optional. User feedback value (e.g., "positive", "negative"). Maximum length 16 characters.
- `user_feedback_text`: String. Optional. Additional text feedback from the user.

#### Example request {#example-request-1}

```json
{
  "elegoo_user_id": "ELEGOO_USER_001",
  "access_token": "your_access_token_here",
  "messages": "[{\"role\":\"user\",\"content\":\"What slicing settings should I use for PLA?\"},{\"role\":\"assistant\",\"content\":\"I can help you determine the best slicing settings for PLA...\"}]",
  "machine_name": "Elegoo Neptune 4",
  "filament_name": "PLA Generic",
  "print_process_name": "0.20mm Standard",
  "slicing_settings_json": "{\"temperature\":[\"220\"],\"layer_height\":[\"0.2\"]}"
}
```

### Response {#response-1}

#### Status code: `201` {#status-code-201}

Chat session was created successfully.

#### Body {#body-2}

```json
{
  "id": 123,
  "messages": "[{\"role\":\"user\",\"content\":\"What slicing settings should I use for PLA?\"},{\"role\":\"assistant\",\"content\":\"I can help you determine the best slicing settings for PLA...\"}]",
  "machine_name": "Elegoo Neptune 4",
  "filament_name": "PLA Generic",
  "print_process_name": "0.20mm Standard",
  "slicing_settings_json": "{\"temperature\":[\"220\"],\"layer_height\":[\"0.2\"]}",
  "user_feedback": null,
  "user_feedback_text": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

- `id`: Integer. Unique identifier for the newly created chat session.
- `messages`: String. JSON-encoded array of chat messages as provided in the request.
- `machine_name`: String. Optional. Machine name as provided in the request.
- `filament_name`: String. Optional. Filament name as provided in the request.
- `print_process_name`: String. Optional. Print process name as provided in the request.
- `slicing_settings_json`: String. Optional. Slicing settings JSON as provided in the request.
- `user_feedback`: String. Optional. User feedback as provided in the request.
- `user_feedback_text`: String. Optional. User feedback text as provided in the request.
- `created_at`: String. ISO 8601 timestamp indicating when the chat was created.
- `updated_at`: String. ISO 8601 timestamp indicating when the chat was last updated (same as `created_at` for new chats).

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully due to validation errors.

#### Body {#body-3}

```json
{
  "messages": ["This field is required."]
}
```

or

```json
{
  "messages": ["This field may not be blank."]
}
```

#### Status code: `401` {#status-code-401}

Authentication failed. This can occur when:
- Missing `elegoo_user_id` or `access_token`
- Invalid credentials or expired access token

#### Body {#body-4}

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

## Usage Examples {#usage-examples}

### Create a new chat session {#create-a-new-chat-session}

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/chats/ \
  -H "Content-Type: application/json" \
  -d '{
    "elegoo_user_id": "ELEGOO_USER_001",
    "access_token": "your_access_token_here",
    "messages": "[{\"role\":\"user\",\"content\":\"What are the best settings for printing with PETG?\"}]",
    "machine_name": "Elegoo Neptune 4",
    "filament_name": "PETG Generic"
  }'
```

### Retrieve all chat sessions {#retrieve-all-chat-sessions}

```bash
curl -X GET "https://elegoo-app.obico.io/ent/partners/api/elegoo/chats/?elegoo_user_id=ELEGOO_USER_001&access_token=your_access_token_here"
```

### Create a chat session with query parameters {#create-a-chat-session-with-query-parameters}

```bash
curl -X POST "https://elegoo-app.obico.io/ent/partners/api/elegoo/chats/?elegoo_user_id=ELEGOO_USER_001&access_token=your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": "[{\"role\":\"user\",\"content\":\"How do I fix warping?\"}]",
    "machine_name": "Elegoo Neptune 4"
  }'
```

## Notes {#notes}

- The `messages` field must be a valid JSON-encoded string containing an array of message objects. Each message must have a `role` and `content` field.
- The `slicing_settings_json` field, if provided, should be a valid JSON-encoded string.
- Chat sessions are scoped to the authenticated user. Users can only access their own chat sessions.
- The `id` field is automatically generated and cannot be specified in the POST request.
- The `created_at` and `updated_at` timestamps are automatically managed by the system.

:::tip
Make sure to register your user credentials using the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) before calling the chats API.
:::

:::note
The AI assistant is integrated into JusPrin, a 3D printing slicer derived from OrcaSlicer. It inherits all capabilities of OrcaSlicer and functions exactly the same, with additional improvements. Any feature or functionality available in OrcaSlicer is also present in JusPrin.
:::



