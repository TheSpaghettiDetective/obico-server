# OAuth 2.0 Integration Guide

This guide explains how to integrate your application with Obico using OAuth 2.0 to authenticate and authorize users.

## Overview

Obico implements OAuth 2.0 using the Authorization Code Grant flow. This allows your application to:

- Authenticate users via their Obico accounts
- Access the Obico API on behalf of users
- Perform actions like querying printer status, uploading G-Code files, and more

## Prerequisites

Before you begin, you'll need:

1. Access to an Obico server instance
2. OAuth application credentials (client ID and client secret)

## Obtaining OAuth Credentials

To integrate your application with Obico, you'll need to obtain OAuth credentials from OBICO.

**Contact OBICO Support:**

Email: **support@obico.io**

Please include the following information in your request:

- **Application Name**: A descriptive name for your application
- **Application Description**: Brief description of what your application does
- **Client Type**: `Confidential` (for server-side apps) or `Public` (for mobile/SPA apps)
- **Redirect URIs**: The callback URL(s) where users will be redirected after authorization

Once approved, you will receive:

- `client_id` - Public identifier for your app
- `client_secret` - Secret key (keep this secure, only for confidential clients)

## OAuth 2.0 Authorization Flow

### Step 1: Redirect User to Authorization Endpoint

Direct the user's browser to the authorization endpoint:

```
GET /o/authorize/
```

**Query Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `client_id` | Yes | Your application's client ID |
| `response_type` | Yes | Must be `code` |
| `redirect_uri` | Yes | Must match one of your registered redirect URIs |
| `scope` | No | Space-separated list of scopes (default: `read write`) |
| `state` | Recommended | Random string to prevent CSRF attacks |

**Example:**

```
https://app.obico.io/o/authorize/?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://your-app.com/callback&scope=read%20write&state=random_state_string
```

### Step 2: User Grants Permission

The user will see a consent page asking them to authorize your application. The page displays:

- Your application name
- Requested permissions (e.g., query printer status, upload G-Code, access printer page)

### Step 3: Handle the Callback

After the user grants permission, they'll be redirected to your `redirect_uri` with an authorization code:

```
https://your-app.com/callback?code=AUTHORIZATION_CODE&state=random_state_string
```

**Important:** Verify that the `state` parameter matches the one you sent to prevent CSRF attacks.

### Step 4: Exchange Code for Access Token

Make a POST request to the token endpoint to exchange the authorization code for an access token:

```
POST /o/token/
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `grant_type` | Yes | Must be `authorization_code` |
| `code` | Yes | The authorization code from step 3 |
| `redirect_uri` | Yes | Must match the redirect_uri from step 1 |
| `client_id` | Yes | Your application's client ID |
| `client_secret` | Yes* | Your application's client secret (*required for confidential clients) |

**Example Request:**

```bash
curl -X POST https://app.obico.io/o/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTHORIZATION_CODE" \
  -d "redirect_uri=https://your-app.com/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Example Response:**

```json
{
  "access_token": "abc123xyz...",
  "token_type": "Bearer",
  "expires_in": 3153600000,
  "scope": "read write"
}
```

## Using the Access Token

Once you have an access token, you can make authenticated API requests using either method:

### Method 1: Authorization Header (Recommended)

```bash
curl https://app.obico.io/api/v1/printers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Method 2: X-API-KEY Header

```bash
curl https://app.obico.io/api/v1/printers/ \
  -H "X-API-KEY: YOUR_ACCESS_TOKEN"
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read access to user data and printer information |
| `write` | Write access to modify settings, upload files, and control printers |

## Token Expiration

Access tokens are configured to be long-lived (default: 100 years). However, tokens can be revoked by the user or administrator at any time. Your application should handle `401 Unauthorized` responses gracefully.

## Revoking Tokens

To revoke an access token:

```
POST /o/revoke_token/
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `token` | Yes | The access token to revoke |
| `client_id` | Yes | Your application's client ID |
| `client_secret` | Yes* | Your application's client secret (*for confidential clients) |

## API Reference

Once authenticated, you can access the following API endpoints. All endpoints are prefixed with `https://app.obico.io`.

### User

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me/` | Get current user's profile |
| PATCH | `/api/v1/users/me/` | Update current user's profile |

### Printers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/printers/` | List all printers |
| GET | `/api/v1/printers/{id}/` | Get specific printer |
| PATCH | `/api/v1/printers/{id}/` | Update printer settings |
| DELETE | `/api/v1/printers/{id}/` | Delete printer |
| POST | `/api/v1/printers/{id}/archive/` | Archive a printer |
| POST | `/api/v1/printers/{id}/cancel_print/` | Cancel ongoing print |
| POST | `/api/v1/printers/{id}/pause_print/` | Pause ongoing print |
| POST | `/api/v1/printers/{id}/resume_print/` | Resume paused print |
| POST | `/api/v1/printers/{id}/mute_current_print/` | Mute current print alerts |
| POST | `/api/v1/printers/{id}/acknowledge_alert/` | Acknowledge failure alert |

### Prints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/prints/` | List print history |
| GET | `/api/v1/prints/{id}/` | Get specific print |
| PATCH | `/api/v1/prints/{id}/` | Update print |
| DELETE | `/api/v1/prints/{id}/` | Delete print |
| POST | `/api/v1/prints/bulk_delete/` | Bulk delete prints |
| GET | `/api/v1/prints/{id}/prediction_json/` | Get prediction data for a print |
| GET | `/api/v1/prints/stats/` | Get print statistics |

### G-Code Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/g_code_files/` | List G-Code files |
| GET | `/api/v1/g_code_files/{id}/` | Get specific G-Code file |
| POST | `/api/v1/g_code_files/` | Upload new G-Code file |
| PATCH | `/api/v1/g_code_files/{id}/` | Update G-Code file |
| DELETE | `/api/v1/g_code_files/{id}/` | Delete G-Code file |
| POST | `/api/v1/g_code_files/bulk_delete/` | Bulk delete files |
| POST | `/api/v1/g_code_files/bulk_move/` | Bulk move files to folder |

### G-Code Folders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/g_code_folders/` | List G-Code folders |
| GET | `/api/v1/g_code_folders/{id}/` | Get specific folder |
| POST | `/api/v1/g_code_folders/` | Create new folder |
| PATCH | `/api/v1/g_code_folders/{id}/` | Update folder |
| DELETE | `/api/v1/g_code_folders/{id}/` | Delete folder |
| POST | `/api/v1/g_code_folders/bulk_delete/` | Bulk delete folders |
| POST | `/api/v1/g_code_folders/bulk_move/` | Bulk move folders |

### AI Assistant (JusPrin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jusprin/api/me/` | Get user info with AI credits |
| GET | `/jusprin/api/chats/` | List chat sessions |
| POST | `/jusprin/api/chats/` | Create new chat session |
| GET | `/jusprin/api/chats/{id}/` | Get specific chat |
| PATCH | `/jusprin/api/chats/{id}/` | Update chat |
| DELETE | `/jusprin/api/chats/{id}/` | Delete chat |
| POST | `/jusprin/api/chats/messages/` | Send message to AI (uses AI credits) |
| POST | `/jusprin/api/plate_analysis/` | Analyze 3D printer plate (uses AI credits) |
| POST | `/jusprin/api/contact_support/` | Send support request |

## Code Examples

### Python

```python
import requests
from urllib.parse import urlencode

# Configuration
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "https://your-app.com/callback"
OBICO_SERVER = "https://app.obico.io"

# Step 1: Generate authorization URL
def get_authorization_url(state):
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "read write",
        "state": state
    }
    return f"{OBICO_SERVER}/o/authorize/?{urlencode(params)}"

# Step 4: Exchange code for token
def exchange_code_for_token(code):
    response = requests.post(
        f"{OBICO_SERVER}/o/token/",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    return response.json()

# Using the token
def get_printers(access_token):
    response = requests.get(
        f"{OBICO_SERVER}/api/v1/printers/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()
```

### JavaScript

```javascript
const CLIENT_ID = 'your_client_id';
const CLIENT_SECRET = 'your_client_secret';
const REDIRECT_URI = 'https://your-app.com/callback';
const OBICO_SERVER = 'https://app.obico.io';

// Step 1: Generate authorization URL
function getAuthorizationUrl(state) {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    response_type: 'code',
    redirect_uri: REDIRECT_URI,
    scope: 'read write',
    state: state
  });
  return `${OBICO_SERVER}/o/authorize/?${params}`;
}

// Step 4: Exchange code for token
async function exchangeCodeForToken(code) {
  const response = await fetch(`${OBICO_SERVER}/o/token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: REDIRECT_URI,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET
    })
  });
  return response.json();
}

// Using the token
async function getPrinters(accessToken) {
  const response = await fetch(`${OBICO_SERVER}/api/v1/printers/`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return response.json();
}
```

## Error Handling

### Common OAuth Errors

| Error | Description |
|-------|-------------|
| `invalid_client` | Invalid client_id or client_secret |
| `invalid_grant` | Authorization code is invalid, expired, or already used |
| `invalid_redirect_uri` | Redirect URI doesn't match registered URIs |
| `access_denied` | User denied the authorization request |

### API Errors

| Status Code | Description |
|-------------|-------------|
| `401 Unauthorized` | Token is invalid, expired, or revoked |
| `403 Forbidden` | Token doesn't have required scope |
| `404 Not Found` | Resource doesn't exist or user doesn't have access |

## Security Best Practices

1. **Always use HTTPS** in production environments
2. **Store tokens securely** - never expose in client-side code or logs
3. **Use the `state` parameter** to prevent CSRF attacks
4. **Validate redirect URIs** - ensure they match exactly
5. **Use confidential clients** when possible (server-side applications)
6. **Handle token revocation** - be prepared for tokens to become invalid

## Support

For questions or issues with OAuth integration, please contact the Obico server administrator or refer to the [django-oauth-toolkit documentation](https://django-oauth-toolkit.readthedocs.io/).
