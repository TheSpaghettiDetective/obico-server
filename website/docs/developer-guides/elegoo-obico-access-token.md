---
title: Elegoo-Obico Access Token API
---

The APIs documented on this page are designed for Elegoo partners to manage access tokens for their custom authentication system.

## Authentication {#authentication}

All APIs are authenticated by the partner's authentication token in the HTTP request header:

`Authorization: Token XXX`

:::tip
Please contact Obico team to obtain your partner authentication token.
:::

## Endpoint {#endpoint}

- `https://app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.

## POST `/ent/partners/api/elegoo/access_token/` {#post-entpartnersapielegooaccess-token}

Creates a new Elegoo custom authentication record.

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `serial_no` (required): A unique identifier for the device. Max 256 characters.
- `access_token` (required): The access token for the device. Max 512 characters.
- `expired_at` (required): ISO 8601 formatted datetime string for token expiration.

#### Example request {#example-request}

```json
{
  "serial_no": "ELEGOO_DEVICE_001",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expired_at": "2025-12-31T23:59:59Z"
}
```

### Response {#response}

#### Status code: `201` {#status-code-201}

Access token record was created successfully.

#### Body {#body}

```json
{
  "code": 200,
  "msg": "success"
}
```

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully due to missing required parameters or invalid data format.

#### Body {#body-1}

```json
{
  "error": "serial_no, access_token, and expired_at are required"
}
```

or

```json
{
  "error": "Invalid expired_at. Use ISO 8601."
}
```

#### Status code: `401` {#status-code-401}

Partner authentication token is not valid. Contact Obico team member.

#### Body {#body-3}

```json
{
  "error": "Invalid or Inactive Token",
  "is_authenticated": "False"
}
```

## PATCH `/ent/partners/api/elegoo/access_token/` {#patch-entpartnersapielegooaccess-token}

Updates an existing Elegoo custom authentication record.

### Request {#request-1}

This PATCH request should be sent as `application/json` format.

#### Query parameters {#query-parameters}

- `serial_no` (optional): The serial number to identify the record to update. Can also be provided in the request body.

#### Body parameters {#body-parameters-1}

- `serial_no` (required if not in query): The serial number to identify the record to update.
- `access_token` (optional): New access token to update.
- `expired_at` (optional): New expiration datetime in ISO 8601 format. Cannot be empty or null.

#### Example request {#example-request-1}

```json
{
  "serial_no": "ELEGOO_DEVICE_001",
  "access_token": "new_updated_token_xyz789",
  "expired_at": "2026-01-31T23:59:59Z"
}
```

### Response {#response-1}

#### Status code: `200` {#status-code-200}

Access token record was updated successfully.

#### Body {#body-2}

```json
{
  "code": 200,
  "msg": "success"
}
```

#### Status code: `400` {#status-code-400-1}

API request was NOT processed successfully due to missing required parameters or invalid data format.

#### Body {#body-4}

```json
{
  "error": "serial_no is required"
}
```

or

```json
{
  "error": "Invalid expired_at. Use ISO 8601."
}
```

or

```json
{
  "error": "expired_at cannot be empty or null"
}
```

#### Status code: `404` {#status-code-404}

The specified serial number was not found.

#### Body {#body-5}

```json
{
  "error": "Auth record not found"
}
```

#### Status code: `401` {#status-code-401-1}

Partner authentication token is not valid. Contact Obico team member.

#### Body {#body-6}

```json
{
  "error": "Invalid or Inactive Token",
  "is_authenticated": "False"
}
```

## Usage Examples {#usage-examples}

### Creating a new access token

```bash
curl -X POST https://app.obico.io/ent/partners/api/elegoo/access_token/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "serial_no": "ELEGOO_DEVICE_001",
    "access_token": "your_access_token_here",
    "expired_at": "2025-12-31T23:59:59Z"
  }'
```

### Updating an existing access token

```bash
curl -X PATCH "https://app.obico.io/ent/partners/api/elegoo/access_token/?serial_no=ELEGOO_DEVICE_001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "access_token": "new_updated_token",
    "expired_at": "2026-01-31T23:59:59Z"
  }'
```

