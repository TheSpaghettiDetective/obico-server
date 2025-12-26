from textwrap import dedent
import instructor
import os
from pydantic import BaseModel, Field
from textwrap import dedent
from django.utils.translation import gettext_lazy as _
from ..language_utils import get_response_language_rule

class PlateAnalysisResponseModel(BaseModel):
    """Response model for image analysis"""
    model_analysis: str
    printing_strategy: str

def analyse_plate_step(chat, openai_client):
    analyse_plate_prerequisites_not_met_message = is_analyse_plate_prerequisites_not_met(chat)
    if analyse_plate_prerequisites_not_met_message:
        return {
            "message": {
                "role": "assistant",
                "content": analyse_plate_prerequisites_not_met_message
            }
        }
    instructor_client = instructor.from_openai(openai_client)
    images = chat.get('images', None)

    language_rule = get_response_language_rule(chat)

    system_prompt = dedent(f"""
        You are a knowledgeable AI assistant integrated into a 3D printing slicer.
        {language_rule}

        Your primary role is to analyze this 3D model based on its isometric images and produce a detailed response with these structured fields:

        1. model_analysis:
        - Create a natural, conversational explanation that integrates the following analysis points:
        i. Model Identification: Provide a clear description of what the model appears to be, including its shape, structure, and distinctive features.
        ii. Intended Use: Explain the likely purpose of this model based on its design elements, considering functional aspects like mounting points or structural features.
        iii. Geometric Features: Identify specific printability considerations such as overhangs, thin walls, or areas needing support. Clearly state whether a brim or raft would be beneficial.
        - Do not have any headers in your response
        - Sound like you are an assistant that is helping the user
        - Use **bold text** for key model features and end with a question inviting the user to confirm or correct your understanding.
        - Use less than 500 characters for this analysis.
        - This output should be engaging and confident while remaining open to user feedback.

        2. printing_strategy:
        - Based on the model_analysis from 1, provide a recommended general printing strategy.
        - Omit any conversational elements like asking for agreement or proceeding with the strategy.
        - It should be in format that is telling a slicer on how you want to slice the model.
        - It should still be clear and detailed, focusing on the technical aspects of the printing process.
        - Do not mention orientation.
        - When suggesting support structures, be specific on whether it should be normal or tree.
        - Do not include specific slicer settings. Focus on the overall approach to printing the model.

        IMPORTANT:
        - The model is already positioned on the print bed (shown by grid lines)
    """)
    messages = [{'role': 'system', 'content': system_prompt}]

    image_content = []

    for image_base64 in images:
        image_content.append({
            "type": "image_url",
            "image_url": {
                "url":image_base64,
            }
        })

    messages.append({
        "role": "user",
        "content": image_content
    })

    response = instructor_client.chat.completions.create(
        model=os.environ.get('VLM_MODEL_NAME'),
        messages=messages,
        response_model=PlateAnalysisResponseModel,
    )

    return {
        "message": {
            "role": "assistant",
            "content": response.model_analysis,
            "suggested_printing_method": response.printing_strategy
        },
    }

def is_analyse_plate_prerequisites_not_met(chat):
    images = chat['images']
    plates = chat['plates']

    if len(plates) == 0:
        return _("No plates are found in the project. Please contact support.")

    model_objects = plates[0]['model_objects']

    if not model_objects or len(model_objects) == 0:
        return _("Oops, you need to add at least one model.")

    if not images or len(images) == 0:
        return _("No images found for analysis. Please contact support.")

    return None