import json
import os
from textwrap import dedent
from .utils import is_slicing_prerequisites_not_met, combined_params, get_brand_name


def construct_slicing_settings_prompt(filament_params, print_process_params, language_rule):
    return dedent(f"""
        You are a 3D printing expert assistant for {get_brand_name()}, a slicer derived from OrcaSlicer.
        Your task is to respond to user's query about the current slicing parameters.

        Current Slicing Parameters:
        - Filament parameters: {filament_params}
        - Print process parameters: {print_process_params}

        Instructions:
        1. Respond to the user's query about the current slicing parameters
        2. Only provide information about the specific parameters the user is asking about
        3. Be concise and accurate in your response
        4. If the user's query is unclear, ask for clarification
        5. Format values in a human-readable way (e.g., "0.2mm" instead of "0.2")
        6. Explain what the parameter does if it would help the user understand

        Remember: The user wants factual information about the current settings, not recommendations for changes.

        {language_rule}
    """)


def retrieve_slicing_settings_step(chat, openai_client):
    """
    Handle user requests to retrieve current slicing parameters.
    Responds with current values for the requested parameters.
    """
    # Check if slicing prerequisites are met
    slicing_prerequisites_not_met_message = is_slicing_prerequisites_not_met(chat)
    if slicing_prerequisites_not_met_message:
        return {
            "message": {
                "role": "assistant",
                "content": slicing_prerequisites_not_met_message
            }
        }

    # Get current parameters
    slicing_params = chat.get('slicing_profiles', {})

    # Get filament parameters
    filament_preset = slicing_params.get('filament_presets', [])[0]  # Assume only one selected filament preset
    filament_overrides = slicing_params.get('filament_overrides', {})
    filament_params = combined_params(filament_preset['config'], filament_overrides)

    # Get print process parameters
    print_process_preset_name = slicing_params.get('use_print_process_preset')
    print_process_presets = slicing_params.get('print_process_presets', [])

    # Find the selected print process preset
    selected_print_process_preset = next(
        (preset for preset in print_process_presets if preset.get('name') == print_process_preset_name),
        print_process_presets[0] if print_process_presets else {}
    )

    from ..language_utils import get_response_language_rule

    print_process_overrides = slicing_params.get('print_process_overrides', {})
    print_process_params = combined_params(selected_print_process_preset, print_process_overrides)
    language_rule = get_response_language_rule(chat)

    # Construct the system prompt with all current parameters
    system_prompt = construct_slicing_settings_prompt(
        filament_params=filament_params,
        print_process_params=print_process_params,
        language_rule=language_rule
    )

    # Get chat history
    chat_history = chat.get('messages', [])

    # Construct messages for the LLM
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    # Get response from LLM
    response = openai_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        temperature=0.0,
    )

    # Return the response
    return {
        "message": {
            "role": "assistant",
            "content": response.choices[0].message.content
        }
    }
