import json
import os
from textwrap import dedent
from .determine_slicing_settings_step import determine_slicing_settings_step
from .guide_print_issue_troubleshooting_step import guide_print_issue_troubleshooting_step
from .retrieve_slicing_settings_step import retrieve_slicing_settings_step
from .utils import add_agent_action_to_message, get_new_lines_as_string, get_brand_name


def get_tools():
    brand_name = get_brand_name()
    return [
        {
            "name": "start_chat_over",
            "description": f"Start a new chat with {brand_name} AI assistant.",
            "parameters": {}
        },
        {
            "name": "slice_model",
            "description": "Slice the model using the current slicing parameters. Use this when the user explicitly asks to start slicing the model.",
            "parameters": {}
        },
        {
            "name": "auto_orient_all_models",
            "description": "Automatically orient all models to minimize the need for supports. Note that this does not allow for specific manual orientation requests.",
            "parameters": {}
        },
        {
            "name": "auto_arrange_all_models",
            "description": "Automatically arrange all models on the print bed.",
            "parameters": {}
        },
        {
            "name": "add_printers",
            "description": "Add new printers to the slicer. Use this when the user explicitly asks to register new printers.",
            "parameters": {}
        },
        {
            "name": "change_printer",
            "description": "Change the printer currently selected in the slicer. Use this when the user asks to switch to a different printer.",
            "parameters": {}
        },
        {
            "name": "add_filaments",
            "description": "Add new filaments to the slicer. Use this when the user explicitly asks to register new filaments.",
            "parameters": {}
        },
        {
            "name": "change_filament",
            "description": "Change the filament currently selected in the slicer. Use this when the user asks to switch to a different filament.",
            "parameters": {}
        },
        {
            "name": "contact_support",
            "description": f"Direct the user to contact {brand_name} support. Use this if the user reports an error with {brand_name}.",
            "parameters": {}
        },
        {
            "name": "determine_slicing_settings",
            "description": (
                "Analyze the user's request to determine the optimal slicing settings. "
                "This includes requests for adjusting speed, quality, wall thickness, or other slicing parameters, "
                "as well as general requests like 'I want a faster print' or 'optimize for strength.' "
                "Use this tool when the user's query indicates they want to modify or optimize slicing settings."
            ),
            "parameters": {}
        },
        {
            "name": "retrieve_slicing_settings",
            "description": (
                "Retrieve the current value of specific slicing parameters. Use this tool when the user explicitly asks "
                "about the current setting for parameters like speed, quality, wall thickness, adhesion, support, infill, etc., "
                "without expressing a desire to change them."
            ),
            "parameters": {}
        },
        {
            "name": "guide_print_issue_troubleshooting",
            "description": (
                "Guide the user through troubleshooting a printing issue. Use this when the user's request is to seek help in troubleshooting a printing issue."
            ),
            "parameters": {}
        }
    ]


def summarize_chat_history(chat, openai_client):
    chat_history = chat.get('messages', [])
    existing_summary = None # TODO: Implement continuation summary

    new_lines = []
    while len(chat_history) > 5:
        message = chat_history.pop(0)
        new_lines.append(message)

    new_lines = get_new_lines_as_string(new_lines)

    system_prompt = f"""Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary. Do not over-summarise.

        EXAMPLE
        Current summary:
        The User asks what the Assistant thinks of artificial intelligence. The Assistant thinks artificial intelligence is a force for good.

        New lines of conversation:
        User: Why do you think artificial intelligence is a force for good?
        Assistant: Because artificial intelligence will help humans reach their full potential.

        New summary:
        The User asks what the Assistant thinks of artificial intelligence. The Assistant thinks artificial intelligence is a force for good because it will help humans reach their full potential.
        END OF EXAMPLE

        Current summary:
        {existing_summary}

        New lines of conversation:
        {new_lines}

        New summary:
    """

    messages = [{'role': 'system', 'content': system_prompt}]

    response = openai_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        temperature=0.0,
    )

    return {
        "updated_chat_history": chat_history,
        "summarized_chat_history": response.choices[0].message.content,
    }

def query_intent_checking_step(chat, openai_client):

    def start_chat_over_tool(message):
        add_agent_action_to_message(message, "start_chat_over", {})

    def slice_model_tool(message):
        add_agent_action_to_message(message, "slice_model", {})

    def add_printers_tool(message):
        add_agent_action_to_message(message, "add_printers", {})

    def change_printer_tool(message):
        add_agent_action_to_message(message, "change_printer", {})

    def add_filaments_tool(message):
        add_agent_action_to_message(message, "add_filaments", {})

    def change_filament_tool(message):
        add_agent_action_to_message(message, "change_filament", {})

    def contact_support_tool(message):
        add_agent_action_to_message(message, "contact_support", {})

    def auto_orient_tool(message):
        add_agent_action_to_message(message, "auto_orient_all_models", {})

    def auto_arrange_tool(message):
        add_agent_action_to_message(message, "auto_arrange_all_models", {})

    def determine_slicing_settings_tool():
        return determine_slicing_settings_step(chat, openai_client)

    def retrieve_slicing_settings_tool():
        return retrieve_slicing_settings_step(chat, openai_client)

    def guide_print_issue_troubleshooting_tool():
        return guide_print_issue_troubleshooting_step(chat, openai_client)

    def call_function(initial_message, name, args=None):
        assistant_message = {
            "role": "assistant",
            "content": initial_message
        }
        if name == "start_chat_over":
            start_chat_over_tool(assistant_message)
        elif name == "slice_model":
            slice_model_tool(assistant_message)
        elif name == "add_printers":
            add_printers_tool(assistant_message)
        elif name == "change_printer":
            change_printer_tool(assistant_message)
        elif name == "add_filaments":
            add_filaments_tool(assistant_message)
        elif name == "change_filament":
            change_filament_tool(assistant_message)
        elif name == "contact_support":
            contact_support_tool(assistant_message)
        elif name == "auto_orient_all_models":
            auto_orient_tool(assistant_message)
        elif name == "auto_arrange_all_models":
            auto_arrange_tool(assistant_message)
        elif name == "determine_slicing_settings":
            return determine_slicing_settings_tool()
        elif name == "retrieve_slicing_settings":
            return retrieve_slicing_settings_tool()
        elif name == "guide_print_issue_troubleshooting":
            return guide_print_issue_troubleshooting_tool()

        return {
            "message": assistant_message
        }

    chat_history = chat.get('messages', [])

    summarized_chat_history = None
    user_messages = [msg for msg in chat_history if msg.get('role') == 'user']
    if len(user_messages) >= 4:
        response = summarize_chat_history(chat, openai_client)
        chat_history = response['updated_chat_history']
        summarized_chat_history = response['summarized_chat_history']

    brand_name = get_brand_name()
    system_prompt = dedent(f"""
    You are a knowledgeable AI assistant integrated into {brand_name}, a 3D printing slicer derived from OrcaSlicer.
    {brand_name} inherits all capabilities of OrcaSlicer and functions exactly the same, with additional improvements.
    Always assume that any feature or functionality available in OrcaSlicer is also present in {brand_name}.
    You will be given a summary of the chat history and asked to determine the user's intent based on the context provided.

    Chat History Summary: {summarized_chat_history}

    - If the user's request is to seek help in troubleshooting a printing issue, you MUST call the 'troubleshoot_print_issue' tool.
    - If the user's request involves adjusting or optimizing slicing parameters (e.g., speed, wall thickness, quality, or any other aspect of the slicing process), you MUST call the 'determine_slicing_settings' tool.
    - For queries about specific actions (e.g., slicing a model or printing), use the appropriate tool if their intent is clear.
    - If the query is unrelated to 3D printing, politely notify the user and ask them to try again with a relevant query.
    - If the query is a general question about 3D printing, answer it based on your knowledge.
    - If the intent is unclear or involves multiple intents, ask the user to clarify before making any tool call.

    Contextual Assumption:
    - You are integrated into a slicer, not a general chatbot.
    - Use {brand_name}'s terminology and UI assumptions when explaining anything.
    - Any reference to OrcaSlicer features should be treated as existing within {brand_name}.
    """)

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    tools = get_tools()
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
            },
        }

    tool_name = response.choices[0].message.function_call.name
    tool_args = json.loads(response.choices[0].message.function_call.arguments)

    # Get the initial response with a single action.
    #
    # NOTE: Some OpenAI-compatible providers may return unexpected wrapper metadata
    # inside `function_call.arguments` (e.g. {"request": ...}). We keep passing the
    # parsed dict through as a single `args` object (instead of `**tool_args`) so
    # unknown keys won't crash Python, and future tools can opt-in to reading args.
    return call_function(response.choices[0].message.content, tool_name, tool_args)
