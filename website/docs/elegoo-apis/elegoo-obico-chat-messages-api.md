---
title: Elegoo-Obico Chat Messages API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to interact with Obico's AI-powered chat assistant for 3D printing slicer guidance. This system uses advanced AI models to help users with various tasks including query intent detection, slicing settings determination, and print troubleshooting.


## Authentication {#authentication}

Authentication is performed using user credentials passed as request parameters:

- `elegoo_user_id`: The Elegoo user identifier registered in the system
- `access_token`: The access token associated with the user

These credentials can be included either in the POST request body (JSON) or as query parameters.

:::tip
Use the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) to manage user credentials before using the chat messages API.
:::

## Language Support {#language-support}

API responses can be returned in different languages using the `lang` query parameter. See the [Elegoo-Obico Language Support](./elegoo-obico-language-support.md) documentation for details on supported languages and usage.

**Example:**
```bash
POST /ent/partners/api/elegoo/chats/messages/?lang=zh-CN
```

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/chats/messages/` {#post-entpartnersapielegoochatsmessages}

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `elegoo_user_id`: String. Required for authentication. The Elegoo user identifier. Can also be passed as query parameter.
- `access_token`: String. Required for authentication. The access token for the user. Can also be passed as query parameter.
- `messages`: Array. Required. Chat messages representing the complete conversation history. **The API does not store or retrieve chat history—the client must maintain and send the full history with each request.**
  - Each message object should have:
    - `role`: String. Either `"user"` or `"assistant"`.
    - `content`: String. The message content. Can be empty string but not null.
- `chat_id`: String. Optional. Session identifier for the chat. Used for tracing and analytics only (not for retrieving stored messages).
- `current_workflow`: String. Optional. Specifies the current workflow mode.
  - `"print_troubleshooting"`: Routes to print troubleshooting workflow
  - If not specified or `null`, defaults to query intent checking workflow
- `slicing_profiles`: Object. Optional. Contains slicing configuration information. Required when using `determine_slicing_settings` or `retrieve_slicing_settings` workflows.
  - `filament_presets`: Array of filament preset objects. Exactly one selected preset should be provided.
    - `name`: String. Name of the filament preset.
    - `is_selected`: Boolean. Whether this preset is currently selected.
    - `config`: Object. Filament configuration key-value pairs (e.g., `temperature`, `filament_type`, `flow_ratio`).
  - `print_process_presets`: Array of print process preset objects. All available presets should be included.
    - `name`: String. Name of the print process preset.
    - `is_selected`: Boolean. Whether this preset is currently selected.
    - `config`: Object. Print process configuration key-value pairs (e.g., `layer_height`, `print_speed`, `infill_density`).
  - `filament_overrides`: Object. Optional. Filament-specific override settings applied on top of the selected preset.
  - `print_process_overrides`: Object. Optional. Print process-specific override settings applied on top of the selected preset.
- `plates`: Array. Optional. Contains information about models on the print bed. Required when using `determine_slicing_settings` workflow.
  - `model_objects`: Array of model objects on the plate.
    - `extruder_id`: Integer. The extruder ID for the model (currently only single-extruder prints are supported).
    - `id`: String. Unique identifier for the model.
    - `name`: String. Name of the model file.

#### Example request {#example-request}

```json
{
  "elegoo_user_id": "ELEGOO_USER_001",
  "access_token": "your_access_token_here",
  "chat_id": "chat_session_123",
  "messages": [
    {
      "role": "user",
      "content": "What slicing settings should I use for PLA?"
    },
    {
      "role": "assistant",
      "content": "I can help you determine the best slicing settings for PLA. Let me analyze your current setup..."
    },
    {
      "role": "user",
      "content": "I'm using a 0.4mm nozzle"
    }
  ],
  "current_workflow": null,
  "slicing_profiles": {
    "filament_presets": [
      {
        "name": "PLA Generic",
        "is_selected": true,
        "config": {
          "temperature": ["220"],
          "filament_type": ["PLA"]
        }
      }
    ],
    "print_process_presets": [
      {
        "name": "0.12mm Fine",
        "is_selected": false,
        "config": {
          "layer_height": "0.12"
        }
      },
      {
        "name": "0.20mm Standard",
        "is_selected": true,
        "config": {
          "layer_height": "0.2"
        }
      },
      {
        "name": "0.28mm Draft",
        "is_selected": false,
        "config": {
          "layer_height": "0.28"
        }
      }
    ],
    "filament_overrides": {},
    "print_process_overrides": {}
  },
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

#### Status code: `200` {#status-code-200}

API request was processed successfully.

#### Body {#body}

The response contains a `message` object with the assistant's response:

```json
{
  "message": {
    "role": "assistant",
    "content": "Based on your 0.4mm nozzle and PLA filament, I recommend the following settings...",
    "per_override_explanations": [
      {
        "parameter": "temperature",
        "explanation": "PLA typically prints best at 210-220°C"
      }
    ],
    "agent_actions": [
      {
        "name": "determine_slicing_settings",
        "arguments": {}
      }
    ],
    "slicing_profiles": {
      "use_print_process_preset": "0.20mm Standard",
      "filament_overrides": {
        "temperature": [215]
      },
      "print_process_overrides": {
        "sparse_infill_density": 20,
        "enable_support": 0
      }
    }
  },
  "credit_resp": {
    "code": 0,
    "data": null,
    "msg": "",
    "traceId": "00000000000000000000000000000000"
  }
}
```

#### Response fields {#response-fields}

- `message`: Object. Contains the assistant's response.
  - `role`: String. Always `"assistant"`.
  - `content`: String. The assistant's response message content.
  - `per_override_explanations`: Array. Optional. Provides explanations for parameter overrides. Only present when slicing settings are determined.
    - `parameter`: String. Human-readable name of the parameter that was changed.
    - `explanation`: String. Concise explanation of why this parameter value is recommended.
  - `agent_actions`: Array. Optional. Contains actions the client should perform. Multiple actions can be present.
    - `name`: String. The action name (see [Agent Actions](#agent-actions) below).
    - `arguments`: Object. Action-specific arguments. Structure varies by action type.
  - `slicing_profiles`: Object. Optional. Contains recommended slicing profile changes. Only present when slicing settings are adjusted.
    - `use_print_process_preset`: String. The name of the recommended print process preset to use.
    - `filament_overrides`: Object. Filament parameter overrides to apply on top of the preset. Values are arrays for filament parameters (e.g., `{"temperature": [215]}`).
    - `print_process_overrides`: Object. Print process parameter overrides to apply on top of the preset (e.g., `{"layer_height": 0.2}`).
- `credit_resp`: Object or null. The response from the Elegoo credits API. Contains the result of the credit deduction operation.
  - `code`: Integer. `0` indicates success.
  - `data`: Object or null. Additional data from the credits API.
  - `msg`: String. Message from the credits API.
  - `traceId`: String. Trace identifier for debugging.

### Agent Actions {#agent-actions}

The following agent actions can be returned in the `agent_actions` array:

#### Slicer Control Actions

| Action Name | Description | Arguments |
|-------------|-------------|-----------|
| `slice_model` | Trigger model slicing with current settings | `{}` |
| `auto_orient_all_models` | Auto-orient models to minimize support needs | `{}` |
| `auto_arrange_all_models` | Auto-arrange models on the print bed | `{}` |

#### Printer/Filament Management Actions

| Action Name | Description | Arguments |
|-------------|-------------|-----------|
| `add_printers` | Open interface to add new printers | `{}` |
| `change_printer` | Open interface to change selected printer | `{}` |
| `add_filaments` | Open interface to add new filament presets | `{}` |
| `change_filament` | Open interface to change selected filament | `{}` |

#### Workflow Actions

| Action Name | Description | Arguments |
|-------------|-------------|-----------|
| `determine_slicing_settings` | Indicates slicing settings were determined. Response will include `slicing_profiles` and `per_override_explanations`. | `{}` |
| `retrieve_slicing_settings` | Indicates current slicing settings were retrieved and explained. | `{}` |
| `guide_print_issue_troubleshooting` | Start the print troubleshooting workflow | `{}` |
| `confirm_print_troubleshooting_flow` | Request confirmation to enter troubleshooting mode | `{}` |
| `set_print_troubleshooting_flow` | Indicates the client should set `current_workflow` to `"print_troubleshooting"` for subsequent requests | `{}` |
| `confirm_end_troubleshooting` | Request confirmation to exit troubleshooting mode | `{}` |

#### UI Actions

| Action Name | Description | Arguments |
|-------------|-------------|-----------|
| `contact_support` | Direct user to contact JusPrin support | `{}` |
| `start_chat_over` | Reset the chat conversation | `{}` |
| `ask_user_to_choose_from_options` | Present options for user to select from | `{ "user_options_to_choose_from": ["Option 1", "Option 2"] }` |

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully due to validation errors or processing failures.

#### Body {#body-1}

```json
{
  "error": "Error message"
}
```

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

## Workflows {#workflows}

The API supports different workflows based on the `current_workflow` parameter:

### Query Intent Checking (Default) {#query-intent-checking-default}

When `current_workflow` is not specified or is `null`, the API routes to the query intent checking workflow. This workflow:
- Analyzes user queries to determine intent
- Routes to appropriate sub-workflows:
  - **Determine slicing settings**: When user wants to optimize or adjust slicing parameters
  - **Retrieve slicing settings**: When user asks about current parameter values
  - **Print troubleshooting**: When user reports a print issue
- Provides guidance on slicing settings, model preparation, and general 3D printing questions
- Can trigger various agent actions based on user needs
- Supports chat history summarization for long conversations (4+ user messages)

### Print Troubleshooting {#print-troubleshooting}

When `current_workflow` is set to `"print_troubleshooting"`, the API routes to the print troubleshooting workflow. This workflow:
- Focuses on diagnosing and resolving print issues
- Provides step-by-step troubleshooting guidance
- Analyzes print problems and suggests solutions
- Can suggest slicing parameter adjustments via `slicing_profiles` in the response
- May present options for user to choose from via `ask_user_to_choose_from_options` action
- Tracks whether a solution has been proposed and offers follow-up options

**Note:** When the API returns `set_print_troubleshooting_flow` action, the client should set `current_workflow` to `"print_troubleshooting"` in subsequent requests to continue the troubleshooting session.

## Usage Example {#usage-example}

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/chats/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "elegoo_user_id": "ELEGOO_USER_001",
    "access_token": "your_access_token_here",
    "chat_id": "chat_session_123",
    "messages": [
      {
        "role": "user",
        "content": "What are the best settings for printing with PETG?"
      }
    ],
    "slicing_profiles": {
      "filament_presets": [
        {
          "name": "PETG Generic",
          "is_selected": true,
          "config": {
            "temperature": ["240"],
            "filament_type": ["PETG"]
          }
        }
      ],
      "print_process_presets": [
        {
          "name": "0.20mm Standard",
          "is_selected": true,
          "config": {
            "layer_height": "0.2"
          }
        }
      ]
    },
    "plates": [
      {
        "model_objects": [
          {
            "extruder_id": 1,
            "id": "1",
            "name": "model.stl"
          }
        ]
      }
    ]
  }'
```

### Chat History Management {#chat-history-management}

:::warning Important
The API does **NOT** retrieve chat history from the database. The client is responsible for maintaining and sending the complete conversation history in the `messages` array with each request. The `chat_id` parameter is only used for tracing and analytics purposes, not for retrieving stored messages.
:::

The client should:
- Store the conversation history locally
- Include the full conversation history in the `messages` array with each request
- Append the assistant's response from each API call to the local history before the next request

The API automatically manages long conversations:
- For conversations with 4 or more user messages, the system will internally summarize earlier messages to maintain context while reducing token usage
- Each message should have a valid `role` and `content` field (content can be empty string but not null)

### Applying Slicing Profile Changes {#applying-slicing-profile-changes}

When the response includes `slicing_profiles`, the client should:

1. **Switch preset**: If `use_print_process_preset` is provided, change the active print process preset to the specified one.
2. **Apply filament overrides**: Merge `filament_overrides` with any existing overrides. Note that filament parameter values are arrays (e.g., `{"temperature": [215]}`).
3. **Apply print process overrides**: Merge `print_process_overrides` with any existing overrides (only if the preset hasn't changed; otherwise, start fresh).
4. **Update subsequent requests**: Include the updated overrides in subsequent API requests so the AI has accurate context.

:::tip
Make sure to register your user credentials using the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) before calling the chat messages API.
:::

:::note
The AI assistant is integrated into JusPrin, a 3D printing slicer derived from OrcaSlicer. It inherits all capabilities of OrcaSlicer and functions exactly the same, with additional improvements. Any feature or functionality available in OrcaSlicer is also present in JusPrin.
:::

### Prerequisites for Slicing Operations {#prerequisites}

When using workflows that involve slicing settings (`determine_slicing_settings` or `retrieve_slicing_settings`), the following prerequisites must be met:

1. `slicing_profiles` must be provided with at least one `filament_presets` entry (exactly one selected)
2. `print_process_presets` must include available presets
3. `plates` must contain at least one model object
4. Currently only single-extruder prints are supported (all models must use the same `extruder_id`)

If prerequisites are not met, the API will return an appropriate error message in the `content` field.
