import json
import os
from textwrap import dedent
from typing import Optional, List
import instructor
from pydantic import BaseModel, Field, field_validator
from .determine_slicing_settings_adjustments_step import (
    FilamentParamOverride,
    PrintProcessParamOverride,
    fix_filament_param_override,
    fix_print_process_param_override,
    fix_support_related_param_override,
    fix_brim_related_param_override,
    combined_params
)
from .utils import add_agent_action_to_message, parse_json_string_fields
class PrintTroubleShootingResponse(BaseModel):
    content: str = Field(
        description="Message to display to the user. If parameter adjustments are provided, assume they have already been applied in the slicer."
    )
    filament_param_adjustments: Optional[FilamentParamOverride] = Field(
        default=None,
        description="Filament-related parameter values that will be applied automatically in the slicer (e.g., temperature, retraction, cooling)."
    )
    print_process_param_adjustments: Optional[PrintProcessParamOverride] = Field(
        default=None,
        description="Print process parameter values that will be applied automatically in the slicer (e.g., layer height, print speed, supports)."
    )
    end_troubleshooting: Optional[bool] = Field(
        default=None,
        description="Whether the user intends to end the troubleshooting session, or to change topics"
    )
    user_options_to_choose_from: Optional[List[str]] = Field(
        default=None,
        description="Only provide this field if the user is being asked to explicitly choose between clear options. If no choice is needed, set this to an empty list."
    )
    solution_is_proposed: Optional[bool] = Field(
        default=None,
        description="Whether or not a solution has been proposed in the current message. Set it to True no matter if the solution involves adjusting slicing parameters or not."
    )

    @field_validator(
        "filament_param_adjustments",
        "print_process_param_adjustments",
        "user_options_to_choose_from",
        "end_troubleshooting",
        "solution_is_proposed",
        mode="before",
    )
    @staticmethod
    def _parse_json_string_fields(v):
        return parse_json_string_fields(v)

def get_confirmation_message(chat, openai_client):
    from ..language_utils import get_response_language_rule

    chat_history = chat.get('messages', [])
    language_rule = get_response_language_rule(chat)

    system_prompt = dedent(f"""
        You are an AI assistant helping to confirm a user's intent to troubleshoot a printing issue.
        Your task is to:
        1. Rephrase the user's reported issue clearly and concisely
        2. Ask the user if the print in question was made with the current slicing settings.

        Keep your response brief and focused on these two points.

        {language_rule}
    """)

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    response = openai_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        temperature=0.0,
    )

    assistant_message = {
        "role": "assistant",
        "content": response.choices[0].message.content,
    }

    add_agent_action_to_message(assistant_message, "confirm_print_troubleshooting_flow", {})

    return {
        "message": assistant_message
    }


def guide_print_issue_troubleshooting_step(chat, openai_client):
    # If not in troubleshooting mode, get confirmation first
    if chat.get('current_workflow') != 'print_troubleshooting':
        return get_confirmation_message(chat, openai_client)

    slicing_params = chat.get('slicing_profiles', {})
    filament_preset = slicing_params.get('filament_presets', [])[0]
    prev_filament_overrides = slicing_params.get('filament_overrides', {})
    filament_params = combined_params(filament_preset['config'], prev_filament_overrides)

    print_process_presets = slicing_params.get('print_process_presets', [])
    suggested_print_process_preset = next(
        (preset for preset in print_process_presets if preset.get('is_selected')),
        None
    )
    prev_print_process_overrides = slicing_params.get('print_process_overrides', {})
    print_process_params = combined_params(suggested_print_process_preset, prev_print_process_overrides)

    from ..language_utils import get_response_language_rule

    chat_history = chat.get('messages', [])
    print_process_preset_name = suggested_print_process_preset.get('name')
    language_rule = get_response_language_rule(chat)

    system_prompt = dedent(f"""
        You are a AI assistant integrated into a 3D printing slicer.
        Your sole purpose is to guide the user through the troubleshooting process. If user's intent is not about troubleshooting, you should ask the user if they want to end the troubleshooting session.
        The user reports a printing issue. Your task is to guide the user through the troubleshooting process.

        Given the following slicing parameters:
        - Filament parameters: {filament_params}
        - Print process parameters: {print_process_params}

        Follow these steps:
        1. Determine if the user's intent is to end troubleshooting, or to change topics. If so, ask the user to confirm. Also set the end_troubleshooting field to True.
        2. Determine if the print issue the user reported is clear. If not, respond with a message asking the user to clarify their intent.
        3. Determine all possible causes of the print issue, and how likely each cause is to be the issue. Order the causes from most likely to least likely.
        4. Examine the slicing parameters and determine if they have made some of the causes more or less likely. If so, adjust the likelihood of the causes accordingly.
        5. Based on the causes you have determined, construct a plan for gathering information to narrow down the cause.
        - The plan should be easy to follow. If possible, it should tackle only one cause at a time.
        - If there is one cause that is very likely to be the issue, start with that cause.
        - If there is more than one cause that is equally likely to be the issue, ask the user which cause they want to start with.
        6. If necessary, ask the user to provide more information to help you narrow down the cause.
        7. If gathering more information will involve adjusting slicing settings and slicing again, confirm with the user if they would like to do that. Do NOT set print_process_param_override or filament_param_override at this point.
        8. If the user has confirmed to adjust slicing settings, adjust the parameters by setting them in the print_process_param_override and/or filament_param_override fields. Ask the user to reslice and report back the results.

        Respond in a direct and engaging manner.
        - Avoid referring to 'the user' and speak naturally.
        - Avoid revealing your internal logic.
        - If any slicing parameter adjustments are returned, assume the slicer has already applied them, and reflect this in your language.

        {language_rule}
    """)

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    instructor_client = instructor.from_openai(openai_client)
    response = instructor_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        response_model=PrintTroubleShootingResponse,
        messages=messages,
        temperature=0.0,
    )

    filtered_response = response.model_dump(exclude_none=True)

    assistant_message = {
        "role": "assistant",
        "content": filtered_response.get('content', ''),
    }

    if filtered_response.get('end_troubleshooting'):
        add_agent_action_to_message(assistant_message, "confirm_end_troubleshooting", {})
        return {
            "message": assistant_message
        }

    add_agent_action_to_message(assistant_message, "set_print_troubleshooting_flow", {})
    if filtered_response.get('solution_is_proposed') and \
        not filtered_response.get('user_options_to_choose_from'): # HACK: LLM often set solution_is_proposed when choices are presented, not a solution.
        add_agent_action_to_message(assistant_message, "ask_user_to_choose_from_options", {
            "user_options_to_choose_from": ["It did not fix the problem"]
        })

    if filtered_response.get('user_options_to_choose_from'):
        add_agent_action_to_message(assistant_message, "ask_user_to_choose_from_options", {
            "user_options_to_choose_from": filtered_response.get('user_options_to_choose_from')
        })

        # FIXME: Sometimes the LLM still sets the parameter overrides even if it's just asking for user confirmation.
        # Return early to work around this.
        return {
            "message": assistant_message
        }

    filament_overrides = filtered_response.get('filament_param_adjustments', {})
    print_process_overrides = filtered_response.get('print_process_param_adjustments', {})

    if filament_overrides or print_process_overrides:
        filament_overrides = fix_filament_param_override(filament_overrides)
        print_process_overrides = fix_print_process_param_override(print_process_overrides)
        print_process_overrides = fix_support_related_param_override(print_process_overrides)
        print_process_overrides = fix_brim_related_param_override(print_process_overrides)

        # Final overrides are the new overrides on top of the previous overrides
        prev_filament_overrides = fix_filament_param_override(prev_filament_overrides)
        final_filament_overrides = combined_params(prev_filament_overrides, filament_overrides)
        final_print_process_overrides = combined_params(prev_print_process_overrides, print_process_overrides)

        assistant_message["slicing_profiles"] = {
            "filament_overrides": final_filament_overrides,
            "print_process_overrides": final_print_process_overrides
        }

    return {
        "message": assistant_message
    }
