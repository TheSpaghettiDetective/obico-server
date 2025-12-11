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

## POST `/ent/partners/api/elegoo/chats/messages/` {#post-entpartnersapielegoochatsmessages}

### Request {#request}

This POST request should be sent as `application/json` format.

#### Body parameters {#body-parameters}

- `elegoo_user_id`: The Elegoo user identifier. Required for authentication. Can also be passed as query parameter.
- `access_token`: The access token for the user. Required for authentication. Can also be passed as query parameter.
- `messages`: Array of chat messages representing the conversation history. Required.
  - Each message object should have:
    - `role`: String. Either `"user"` or `"assistant"`.
    - `content`: String. The message content. Can be empty string but not null.
- `chat_id`: Session identifier for the chat. Optional. Used for context tracking.
- `current_workflow`: String. Optional. Specifies the current workflow mode.
  - `"print_troubleshooting"`: Routes to print troubleshooting workflow
  - If not specified, defaults to query intent checking workflow
- `slicing_profiles`: Object. Optional. Contains slicing configuration information.
  - `filament_presets`: Array of filament preset objects.
    - `name`: String. Name of the filament preset.
    - `is_selected`: Boolean. Whether this preset is currently selected.
    - `config`: Object. Filament configuration key-value pairs.
  - `print_process_presets`: Array of print process preset objects.
    - `name`: String. Name of the print process preset.
    - `is_selected`: Boolean. Whether this preset is currently selected.
    - `config`: Object. Print process configuration key-value pairs.
  - `filament_overrides`: Object. Filament-specific override settings.
  - `print_process_overrides`: Object. Print process-specific override settings.
- `plates`: Array of plate objects. Optional. Contains information about models on the print bed.
  - `model_objects`: Array of model objects on the plate.
    - `extruder_id`: Integer. The extruder ID for the model.
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
          "temperature": ["220"]
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
    ]
  }
}
```

- `message`: An object containing the assistant's response.
  - `role`: Always `"assistant"`.
  - `content`: The assistant's response message content.
  - `per_override_explanations`: Array of objects. Optional. Provides explanations for parameter overrides.
    - `parameter`: String. The parameter name being explained.
    - `explanation`: String. Explanation of why this parameter value is recommended.
  - `agent_actions`: Array of objects. Optional. Contains actions the client should perform.
    - `name`: String. The action name. Common values include:
      - `"change_printer"`: Change the selected printer
      - `"slice_model"`: Trigger model slicing
      - `"add_printers"`: Add printers to the setup
      - `"add_filaments"`: Add filament presets
      - `"change_filament"`: Change the selected filament
      - `"contact_support"`: Open support contact interface
      - `"auto_orient_all_models"`: Auto-orient models on the bed
      - `"auto_arrange_all_models"`: Auto-arrange models on the bed
      - `"determine_slicing_settings"`: Determine optimal slicing settings
      - `"retrieve_slicing_settings"`: Retrieve previously determined settings
      - `"guide_print_issue_troubleshooting"`: Start troubleshooting workflow
      - `"start_chat_over"`: Reset the chat conversation
    - `arguments`: Object. Action-specific arguments. Structure varies by action type.

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

## Workflows {#workflows}

The API supports different workflows based on the `current_workflow` parameter:

### Query Intent Checking (Default) {#query-intent-checking-default}

When `current_workflow` is not specified or is null, the API routes to the query intent checking workflow. This workflow:
- Analyzes user queries to determine intent
- Provides guidance on slicing settings, model preparation, and general 3D printing questions
- Can trigger various agent actions based on user needs
- Supports chat history summarization for long conversations (4+ user messages)

### Print Troubleshooting {#print-troubleshooting}

When `current_workflow` is set to `"print_troubleshooting"`, the API routes to the print troubleshooting workflow. This workflow:
- Focuses on diagnosing and resolving print issues
- Provides step-by-step troubleshooting guidance
- Analyzes print problems and suggests solutions

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
            "temperature": ["240"]
          }
        }
      ]
    }
  }'
```

### Chat History Management {#chat-history-management}

The API automatically manages chat history:
- For conversations with 4 or more user messages, the system will summarize earlier messages to maintain context while reducing token usage
- The full conversation history should be included in the `messages` array
- Each message should have a valid `role` and `content` field (content can be empty string but not null)

:::tip
Make sure to register your user credentials using the [Elegoo-Obico User Access Token API](./elegoo-obico-user-access-token.md) before calling the chat messages API.
:::

:::note
The AI assistant is integrated into JusPrin, a 3D printing slicer derived from OrcaSlicer. It inherits all capabilities of OrcaSlicer and functions exactly the same, with additional improvements. Any feature or functionality available in OrcaSlicer is also present in JusPrin.
:::
