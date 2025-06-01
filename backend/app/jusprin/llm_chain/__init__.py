from .query_intent_checking_step import query_intent_checking_step
from .guide_print_issue_troubleshooting_step import guide_print_issue_troubleshooting_step

def run_chain_on_chat(chat, openai_client):
    """
    Input parameters:

    - chat:
    {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm fine, thank you!"}
        ],
        "current_workflow": "print_troubleshooting",  # Optional field to specify the current workflow
        "slicing_profiles": {
            "filament_presets": [
                "name": "Filament name",
                "is_selected": True/False,
                "config": {
                    "key": ["value"],
                }
            ],
            "print_process_presets": [
                {
                    "name": "Print process name",
                    "is_selected": True/False,
                    "config": {
                        "key": "value"
                    }
                }
            ],
            "filament_overrides": {
                "key": ["value"]
            },
            "print_process_overrides": {
                "key": "value"
            },
        },
        "plates": [
            {"model_objects": [
                {"extruder_id": 1,
                "id": "52",
                "name": "Octopus_Head_v6.stl"}
            ]}
        ]
    }

    Return value:
    {
        "message":{
            "role": "assistant",
            "content": "value",
            "per_override_explanations": [
                {
                    "parameter": "value",
                    "explanation": "value"
                }
            ],
            "agent_actions": [
                {
                    "name": "change_printer", # or other agent (client-side) actions such as "slice_model"
                    "arguments": {
                    }
                }
            ],
        }
    }
    """

    # OpenAI API will throw an error if the content is None.
    for message in chat['messages']:
        if message.get('content') is None:
            message['content'] = ''

    # Route to appropriate step based on current workflow
    if chat.get('current_workflow') == 'print_troubleshooting':
        return guide_print_issue_troubleshooting_step(chat, openai_client)

    return query_intent_checking_step(chat, openai_client)
