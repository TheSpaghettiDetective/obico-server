---
title: Elegoo-Obico User Access Token API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to manage user-based access tokens for their custom authentication system.

## Authentication {#authentication}

All APIs are authenticated by the partner's authentication token in the HTTP request header:

`Authorization: Token XXX`

:::tip
Please contact Obico team to obtain your partner authentication token.
:::

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/user_access_token/` {#post-entpartnersapielegoouser-access-token}

Creates a new Elegoo user access token record, or updates an existing one if a record with the same `elegoo_user_id` already exists.

:::tip
This endpoint performs an "upsert" operation - it will create a new record if the `elegoo_user_id` doesn't exist, or update the existing record if it does. This allows you to use a single endpoint for both creating and refreshing access tokens.
:::

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `elegoo_user_id` (required): A unique identifier for the Elegoo user. Max 256 characters.
- `access_token` (required): The access token for the user. Max 512 characters.
- `expire_in` (required): Number of seconds from now until the token expires. Server computes `expired_at`.

#### Example request {#example-request}

```json
{
  "elegoo_user_id": "ELEGOO_USER_001",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expire_in": 86400
}
```

### Response {#response}

#### Status code: `201` {#status-code-201}

A new access token record was created successfully.

#### Body {#body}

```json
{
  "code": 201,
  "msg": "success"
}
```

#### Status code: `200` {#status-code-200}

An existing access token record was updated successfully.

#### Body {#body-2}

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
  "error": "elegoo_user_id, access_token, and expire_in are required"
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
  "error": "expire_in must be > 0 seconds"
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

## Usage Examples {#usage-examples}

### Creating a new access token

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/user_access_token/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "elegoo_user_id": "ELEGOO_USER_001",
    "access_token": "your_access_token_here",
    "expire_in": 86400
  }'
```

Response (201 Created):
```json
{
  "code": 201,
  "msg": "success"
}
```

### Updating an existing access token

To update an existing access token, simply send the same POST request with the same `elegoo_user_id` but with new `access_token` and/or `expire_in` values:

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/user_access_token/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_PARTNER_TOKEN" \
  -d '{
    "elegoo_user_id": "ELEGOO_USER_001",
    "access_token": "new_updated_token",
    "expire_in": 172800
  }'
```

Response (200 OK):
```json
{
  "code": 200,
  "msg": "success"
}
```

:::note
The endpoint automatically determines whether to create or update based on whether the `elegoo_user_id` already exists. You can use the same POST request for both operations - the response status code will indicate whether a new record was created (201) or an existing one was updated (200).
:::
