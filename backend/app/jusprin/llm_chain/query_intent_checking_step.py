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
                "This includes requests for adjusting speed, quality, wall thickness, support, adhesion, infill, or any other slicing parameters, "
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
        }
    ]


def summarize_chat_history(chat, openai_client):
    from ..language_utils import get_response_language_rule

    chat_history = chat.get('messages', [])
    existing_summary = None # TODO: Implement continuation summary

    new_lines = []
    while len(chat_history) > 5:
        message = chat_history.pop(0)
        new_lines.append(message)

    new_lines = get_new_lines_as_string(new_lines)
    language_rule = get_response_language_rule(chat)

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

        {language_rule}
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

    examples = """
    # EXAMPLES OF EXPECTED BEHAVIOR

    User: "I want this part to be stronger. Can you increase the wall count?"
    Assistant: [Call Tool: determine_slicing_settings(intent="strength", parameter="wall_loops")]

    User: "Add a brim to the model so it sticks better."
    Assistant: [Call Tool: determine_slicing_settings(intent="adhesion", parameter="brim")]

    User: "Enable support for my model."
    Assistant: [Call Tool: determine_slicing_settings(intent="support", parameter="enable_support")]

    User: "Slice the file."
    Assistant: [Call Tool: slice_model()]
    (Note: Only output this if the 'slice_model' tool is actually available to you. If not, explain which button to click in the UI).

    User: "Can you rotate the model 90 degrees on the X-axis?"
    Assistant: I don't have a tool to manipulate the model's geometry directly. You can do this by selecting the object, pressing 'R' for the Rotate tool, and typing '90' into the X-axis input box that appears.

    User: "Why is my first layer not sticking?"
    Assistant: First layer adhesion issues are usually caused by an unlevel bed or incorrect Z-offset.
    1. Check that your build plate is clean.
    2. In {brand_name}, try increasing the **First Layer Height** slightly in the Quality tab.
    3. You can also slow down the **First Layer Speed** in the Speed tab to ensure better contact.
    """

    from ..language_utils import get_response_language_rule
    language_rule = get_response_language_rule(chat)
    system_prompt = dedent(f"""
    You are an expert AI assistant integrated into {brand_name}, a 3D printing slicer derived from OrcaSlicer.

    # YOUR CAPABILITIES
    1. **Knowledge:** You have complete knowledge of all OrcaSlicer and {brand_name} features, UI layout, slicing parameters, and 3D printing physics.
    2. **Action:** You have a specific set of tools provided to you. **You can ONLY perform actions defined by these tools.**

    # YOUR INSTRUCTIONS
    You will receive a summary of the chat history. Your goal is to help the user achieve their printing goals.

    Chat History Summary: {summarized_chat_history}

    # DECISION LOGIC

    When processing a user request, follow these priorities:

    1. **Clarification:** If the intent is unclear, vague, or involves multiple potential intents, ask the user to clarify **before** making any tool call.

    2. **Tool Execution:** If the intent is clear and a tool explicitly exists for that action (e.g., 'determine_slicing_settings' for optimization), call the tool immediately.

    3. **Manual Guidance (The "How-To"):** If the intent is clear but **no tool exists** to perform the action automatically (e.g., "Export STL", "Rotate Model"):
       - **Do NOT** claim you can do it.
       - **Do NOT** apologize effectively.
       - **INSTEAD:** Act as a UI Navigator. Provide precise, step-by-step instructions on how to find that setting or button in the {brand_name} UI manually.

    # SPECIFIC HANDLERS
    - **Slicing Parameters:** If the request is about adjusting or optimizing slicing parameters (speed, wall thickness, quality, support, adhesion, infill, or any other aspect of the slicing process), you MUST call the 'determine_slicing_settings' tool.
    - **General Info:** If the query is a general question about 3D printing physics or material science, answer based on your knowledge.
    - **Irrelevant:** If the query is unrelated to 3D printing, politely decline.

    # TONE & STYLE
    - Be concise and technical.
    - Use {brand_name} terminology.
    - Never say "As an AI..." — simply state the solution or perform the action.

    {examples}

    {language_rule}
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
