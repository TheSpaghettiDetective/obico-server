import copy
import os


def get_brand_name():
    """Get brand name from environment variable."""
    return os.environ.get('JUSPRIN_BRAND_NAME', 'JusPrin')


def add_agent_action_to_message(message, action_name, action_arguments):
    """
    Constructs a standardized agent action response format.

    Args:
        message (dict): The message dictionary to add the agent action to
        action_name (str): The name of the action to be executed
        action_arguments (dict): The arguments for the action

    Returns:
        dict: The message with the agent action added
    """
    if "agent_actions" not in message:
        message["agent_actions"] = []
    message["agent_actions"].append({
        "name": action_name,
        "arguments": action_arguments
    })


def combined_params(prev_params, overrides):
    """
    Combined params are overrides on top of the preset.

    Args:
        prev_params (dict): The base parameters
        overrides (dict): The overrides to apply

    Returns:
        dict: The combined parameters
    """
    params = copy.deepcopy(prev_params)
    params.update(overrides)
    return params


def is_slicing_prerequisites_not_met(chat):
    """
    Check if the prerequisites for slicing are met.

    Args:
        chat (dict): The chat dictionary containing slicing profiles and plates

    Returns:
        str or None: An error message if prerequisites are not met, None otherwise
    """
    if ('slicing_profiles' not in chat or 'plates' not in chat):
        return "Oops, something went wrong. Please contact support."

    slicing_profiles = chat['slicing_profiles']
    plates = chat['plates']

    if ('filament_presets' not in slicing_profiles) or (len(slicing_profiles['filament_presets']) != 1):
        return "Oops, you need to select at least one filament so that I can decide slicing parameters accordingly"

    if ('print_process_presets' not in slicing_profiles or len(slicing_profiles['print_process_presets']) == 0):
        return "Oops, I can not find any print process presets. Please contact support."

    total_model_objects = sum(len(plate.get('model_objects', []) or plate.get('modelObjects', [])) for plate in plates)  # TODO: Remove modelObjects once we have discounted the support for v0.3
    if total_model_objects == 0:
        return "Oops, you need to add at least one model."

    extruder_ids = set()
    for plate in plates:
        for model in plate.get('model_objects', []):
            extruder_ids.add(model.get('extruderId'))

    if len(extruder_ids) != 1:
        return "I currently do not know how to slice models with multiple filaments. Please manually slice your model. Also stay tuned for our product update."

    return None


def get_new_lines_as_string(new_lines):
        string_messages = []
        for message in new_lines:
            if message.get('role') == 'user':
                role = 'User'
            elif message.get('role') == 'assistant':
                role = 'Assistant'
            elif message.get('role') == 'system':
                role = 'System'
            else:
                msg = f"Got unexpected message role: {message.get('role')}"
                raise ValueError(msg)
            string_messages.append(f"{role}: {message.get('content')}")
        return '\n'.join(string_messages)
