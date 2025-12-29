---
title: Elegoo-Obico Language Support
unlisted: true
---

The Elegoo-Obico APIs support internationalization (i18n) through the `lang` query parameter. This allows API responses to be returned in the user's preferred language.

## Language Parameter {#language-parameter}

### Usage

The `lang` parameter can be added to any Elegoo partner API request to specify the desired response language. The parameter accepts IETF language tags (e.g., `zh-CN`, `pt-BR`, `en-US`).

### Format

- **Parameter name**: `lang`
- **Format**: IETF language tags (case-insensitive)
- **Examples**: `zh-CN`, `zh-TW`, `pt-BR`, `en-US`, `es`, `de`, `fr`, `it`, `ru`
- **Where to pass**: Query parameter only (`?lang=zh-CN`)

The parameter accepts both hyphenated (`zh-CN`) and underscore-separated (`zh_CN`) formats. Both will be normalized internally.

### How It Works

1. The `lang` query parameter is read from the request URL
2. The value is normalized (underscores converted to hyphens, lowercased)
3. The IETF tag is mapped to a Django language code
4. Django translations are activated for the request
5. All user-facing messages in the API response are returned in the specified language

### Example Requests

#### With language parameter

```bash
POST /ent/partners/api/elegoo/chats/messages/?lang=zh-CN
```

```bash
POST /ent/partners/api/elegoo/plate_analysis/?lang=pt-BR
```

#### Without language parameter

If the `lang` parameter is not provided, the API will use the default language (English).

## Supported Languages {#supported-languages}

The following languages are supported:

| Language Code | Language Name |
|--------------|---------------|
| `en` or `en-US` | English |
| `zh-CN` | Simplified Chinese (简体中文) |
| `zh-TW` | Traditional Chinese (繁體中文) |
| `pt-BR` | Brazilian Portuguese (Português do Brasil) |
| `es` | Spanish (Español) |
| `de` | German (Deutsch) |
| `fr` | French (Français) |
| `it` | Italian (Italiano) |
| `ru` | Russian (Русский) |

### Language Code Mapping

The API accepts IETF language tags and maps them internally to Django language codes:

- `zh-CN` → `zh-cn` (Simplified Chinese)
- `zh-TW` → `zh-tw` (Traditional Chinese)
- `pt-BR` → `pt-br` (Brazilian Portuguese)
- `en-US` or `en` → `en` (English)
- `es` → `es` (Spanish)
- `de` → `de` (German)
- `fr` → `fr` (French)
- `it` → `it` (Italian)
- `ru` → `ru` (Russian)

If an unsupported language code is provided, the API will fall back to the default language (English).

## API Endpoints {#api-endpoints}

The `lang` parameter works with the following Elegoo partner API endpoints:

- `/ent/partners/api/elegoo/chats/` - Chat session management
- `/ent/partners/api/elegoo/chats/messages/` - Chat messages
- `/ent/partners/api/elegoo/plate_analysis/` - Plate analysis

## Example: Complete Request {#example-complete-request}

```bash
POST /ent/partners/api/elegoo/chats/messages/?lang=zh-CN
Content-Type: application/json

{
  "elegoo_user_id": "ELEGOO_USER_001",
  "access_token": "your_access_token_here",
  "messages": [
    {
      "role": "user",
      "content": "What slicing settings should I use?"
    }
  ],
  "chat_id": "chat_session_123"
}
```

### Response in Chinese

```json
{
  "message": {
    "role": "assistant",
    "content": "我可以帮助您确定最佳的切片设置..."
  }
}
```

## Error Messages {#error-messages}

Error messages and validation messages are also translated based on the `lang` parameter:

**Example (English - default):**
```json
{
  "error": "Message is required"
}
```

**Example (Chinese - with `?lang=zh-CN`):**
```json
{
  "error": "消息是必需的"
}
```

## Best Practices {#best-practices}

1. **Always include the `lang` parameter** when you know the user's preferred language
2. **Use IETF language tags** (e.g., `zh-CN` instead of `zh_CN`) for consistency
3. **Handle language fallback** in your client application if an unsupported language is requested
4. **Store user language preference** and include it in all API requests for a consistent experience

## Notes {#notes}

- The language parameter only affects **user-facing messages** in API responses
- **Technical data** (IDs, timestamps, configuration values) are not translated
- The language setting is **per-request** and does not persist across requests
- Language support works with **Elegoo partner API endpoints** (`/ent/partners/api/elegoo/...`)


