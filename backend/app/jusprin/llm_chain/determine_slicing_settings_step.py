from .determine_slicing_settings_adjustments_step import determine_slicing_settings_adjustments_step
import json
import os
from textwrap import dedent
from .utils import is_slicing_prerequisites_not_met


tools = [
    {
        "name": "determine_slicing_settings_adjustments",
        "description": "Determine if there need to be any further slicing settings adjustments to the preset based on the user's request",
        "parameters": {
            "type": "object",
            "properties": {
                "print_process_preset_name": {
                    "type": "string",
                    "description": "The name of the print process preset"
                },
                "explanation": {
                    "type": "string",
                    "description": dedent("""
                        A concise explanation for what preset you have chosen, and why.
                        **Important**:
                        - Avoid referring to 'the user' and speak naturally.
                        - Avoid revealing your internal logic.
                    """)
                }
            },
            "required": ["print_process_preset_name", "explanation"]
        }
    }
]

def determine_slicing_settings_step(chat, openai_client):

    def determine_slicing_settings_adjustments_tool(print_process_preset_name, explanation):
        return determine_slicing_settings_adjustments_step(chat, print_process_preset_name, explanation, openai_client)

    slicing_prerequisites_not_met_message = is_slicing_prerequisites_not_met(chat)
    if slicing_prerequisites_not_met_message:
        return {
            "message": {
                "role": "assistant",
                "content": slicing_prerequisites_not_met_message
            }
        }

    chat_history = chat.get('messages', [])
    slicing_params = chat.get('slicing_profiles', {})
    filament_preset = slicing_params.get('filament_presets', [])[0] # We assume that only the selected filament preset is in the request. This may change in the future.
    process_presets = slicing_params.get('print_process_presets', [])
    process_names = [process["name"] for process in process_presets]

    system_prompt = dedent(f"""
        You are a knowledgeable AI assistant integrated into a 3D printing slicer.
        You are tasked with determining the best slicing settings based on the user's request.

        Follow these steps strictly:

        1. Determine if the user's request is clear. If not, respond with a message asking the user to clarify their intent.
        2. Determine if the current filament preset will work for the user's requirements. If not, explain why and ask if they would like to change the filament, unless they have explicitly said to keep it.
        3. Determine which print process preset is the most appropriate for the user's request.
        4. **Once step 3 has been completed, you must make the tool call to determine if there need to be any further slicing settings adjustments to the preset based on the user's request.** The tool call is mandatory.

        User's current filament selection is:
        - Filament name: {filament_preset.get('name')}
        - Filament type: {filament_preset.get('config', {}).get('filament_type')}

        The valid print process presets are:
        - {process_names}

        **Important**:
        - Avoid referring to 'the user' and speak naturally.
        - Avoid revealing your internal logic.
    """)

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    response = openai_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        functions=tools,
        function_call="auto",
        temperature=0.0,
    )

    if response.choices[0].message.function_call == None:
      return {
        "message": {
          "role": "assistant",
          "content": response.choices[0].message.content
        }
      }

    tool_arguments = json.loads(response.choices[0].message.function_call.arguments)

    return determine_slicing_settings_adjustments_tool(**tool_arguments)
