from .determine_slicing_settings_adjustments_step import determine_slicing_settings_adjustments_step
import instructor
import os
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from textwrap import dedent
from .utils import is_slicing_prerequisites_not_met


def create_slicing_settings_response_model(valid_preset_names: list[str]):
    """Factory function to create a response model with dynamic preset name validation."""

    class DetermineSlicingSettingsResponse(BaseModel):
        print_process_preset_name: Optional[str] = Field(
            default=None,
            description=f"The name of the print process preset. Must be one of: {valid_preset_names}. Set to null if you need to ask for clarification."
        )
        explanation: Optional[str] = Field(
            default=None,
            description=dedent("""
                A concise explanation for what preset you have chosen, and why.
                **Important**:
                - Avoid referring to 'the user' and speak naturally.
                - Avoid revealing your internal logic.
            """)
        )
        clarification_message: Optional[str] = Field(
            default=None,
            description="If the user's request is unclear or you need more information, provide a message asking for clarification. Set print_process_preset_name to null in this case."
        )

        @field_validator('print_process_preset_name')
        @classmethod
        def validate_preset_name(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and v not in valid_preset_names:
                raise ValueError(f"Invalid preset name '{v}'. Must be one of: {valid_preset_names}")
            return v

    return DetermineSlicingSettingsResponse


def determine_slicing_settings_step(chat, openai_client):
    slicing_prerequisites_not_met_message = is_slicing_prerequisites_not_met(chat)
    if slicing_prerequisites_not_met_message:
        return {
            "message": {
                "role": "assistant",
                "content": slicing_prerequisites_not_met_message
            }
        }

    from ..language_utils import get_response_language_rule

    chat_history = chat.get('messages', [])
    slicing_params = chat.get('slicing_profiles', {})
    filament_preset = slicing_params.get('filament_presets', [])[0]  # We assume that only the selected filament preset is in the request. This may change in the future.
    process_presets = slicing_params.get('print_process_presets', [])
    process_names = [process["name"] for process in process_presets]
    language_rule = get_response_language_rule(chat)

    system_prompt = dedent(f"""
        You are a knowledgeable AI assistant integrated into a 3D printing slicer.
        You are tasked with determining the best slicing settings based on the user's request.

        Follow these steps strictly:

        1. Determine if the user's request is clear. If not, set print_process_preset_name to null and provide a clarification_message asking the user to clarify their intent.
        2. Determine if the current filament preset will work for the user's requirements. If not, explain why and ask if they would like to change the filament, unless they have explicitly said to keep it.
        3. Determine which print process preset is the most appropriate for the user's request from the valid options below.

        User's current filament selection is:
        - Filament name: {filament_preset.get('name')}
        - Filament type: {filament_preset.get('config', {}).get('filament_type')}

        The valid print process presets are:
        - {process_names}

        **Important**:
        - You MUST select a preset name EXACTLY as it appears in the valid options list above.
        - Avoid referring to 'the user' and speak naturally.
        - Avoid revealing your internal logic.

        {language_rule}
    """)

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    instructor_client = instructor.from_openai(openai_client)
    ResponseModel = create_slicing_settings_response_model(process_names)

    response = instructor_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        response_model=ResponseModel,
        temperature=0.0,
    )

    # If clarification is needed, return the clarification message
    if response.print_process_preset_name is None:
        return {
            "message": {
                "role": "assistant",
                "content": response.clarification_message or response.explanation or ""
            }
        }

    # Proceed with the validated preset name
    return determine_slicing_settings_adjustments_step(
        chat,
        response.print_process_preset_name,
        response.explanation or "",
        openai_client
    )
