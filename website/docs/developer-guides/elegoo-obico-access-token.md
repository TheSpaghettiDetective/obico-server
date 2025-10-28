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

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.

## POST `/ent/partners/api/elegoo/access_token/` {#post-entpartnersapielegooaccess-token}

Creates a new Elegoo custom authentication record.

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `serial_no` (required): A unique identifier for the device. Max 256 characters. Must be unique across the entire system.
- `access_token` (required): The access token for the device. Max 512 characters.
- `expire_in` (required): Number of seconds from now until the token expires. Server computes `expired_at`.

#### Example request {#example-request}

```json
{
  "serial_no": "ELEGOO_DEVICE_001",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expire_in": 86400
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
  "error": "serial_no, access_token, and expire_in are required"
}
```

or

```json
{
  "error": "expire_in must be an integer number of seconds"
}
```

#### Status code: `409` {#status-code-409}

A record with the same `serial_no` already exists. Each `serial_no` must be unique across the system.

#### Body {#body-409}

```json
{
  "error": "serial_no already exists"
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

- `serial_no` (required): The serial number to identify the record to update. Must be provided as a query parameter.

#### Body parameters {#body-parameters-1}

- `access_token` (optional): New access token to update.
- `expire_in` (required): Number of seconds from now to extend/reset the token expiry. Must be > 0.

:::warning
The `serial_no` field is immutable and cannot be changed. It must be provided as a query parameter only. Including `serial_no` in the request body will result in a 400 error.
:::

#### Example request {#example-request-1}

```json
{
  "access_token": "new_updated_token_xyz789",
  "expire_in": 172800
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
  "error": "serial_no is required as a query parameter"
}
```

or

```json
{
  "error": "serial_no cannot be updated"
}
```

or

```json
{
  "error": "expire_in must be an integer number of seconds"
}
```

or

```json
{
  "error": "expire_in is required and must be provided on PATCH"
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
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/access_token/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "serial_no": "ELEGOO_DEVICE_001",
    "access_token": "your_access_token_here",
    "expire_in": 86400
  }'
```

### Updating an existing access token

```bash
curl -X PATCH "https://elegoo-app.obico.io/ent/partners/api/elegoo/access_token/?serial_no=ELEGOO_DEVICE_001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "access_token": "new_updated_token",
    "expire_in": 172800
  }'
```

:::note
Note that `serial_no` is provided as a query parameter, not in the request body. The `serial_no` field is immutable and cannot be changed once created.
:::

