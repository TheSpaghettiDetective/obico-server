"""Route JusPrin GPT-6 Luna requests through the Responses API.

JusPrin's existing chain and Instructor integration use Chat Completions
objects. Translating at the HTTP boundary preserves those contracts while
using the Responses endpoint and the reasoning setting validated by the
private benchmark. This transport belongs only to JusPrin clients.
"""

import json
import time

import httpx
from openai import OpenAI


def _response_input(messages):
    items = []
    for message in messages:
        if message['role'] == 'tool':
            items.append({
                'type': 'function_call_output',
                'call_id': message['tool_call_id'],
                'output': message.get('content') or '',
            })
            continue
        if message['role'] == 'assistant' and message.get('tool_calls'):
            if message.get('content'):
                items.append({'role': 'assistant', 'content': message['content']})
            for call in message['tool_calls']:
                if call.get('type') != 'function':
                    raise ValueError(f"Unsupported JusPrin tool call: {call.get('type')}")
                items.append({
                    'type': 'function_call',
                    'call_id': call['id'],
                    'name': call['function']['name'],
                    'arguments': call['function']['arguments'],
                })
            continue
        content = message.get('content')
        if isinstance(content, list):
            blocks = []
            for block in content:
                if block['type'] == 'image_url':
                    blocks.append({'type': 'input_image', 'image_url': block['image_url']['url']})
                elif block['type'] == 'text':
                    blocks.append({'type': 'input_text', 'text': block['text']})
                else:
                    raise ValueError(f"Unsupported JusPrin content block: {block['type']}")
            content = blocks
        items.append({'role': message['role'], 'content': content})
    return items


def _responses_request(chat_request):
    supported = {'model', 'messages', 'temperature', 'functions', 'function_call', 'tools', 'tool_choice'}
    unsupported = set(chat_request) - supported
    if unsupported:
        raise ValueError(f"Unsupported JusPrin Chat fields: {sorted(unsupported)}")
    payload = {
        'model': chat_request['model'],
        'input': _response_input(chat_request['messages']),
        'reasoning': {'effort': 'low'},
        'store': False,
        'max_output_tokens': 4096,
    }
    legacy_functions = chat_request.get('functions') or []
    modern_functions = [
        tool['function'] for tool in chat_request.get('tools', [])
        if tool.get('type') == 'function'
    ]
    functions = legacy_functions + modern_functions
    if functions:
        payload['tools'] = [{
            'type': 'function',
            'name': function['name'],
            'description': function.get('description', ''),
            'parameters': function.get('parameters') or {'type': 'object', 'properties': {}},
            'strict': False,
        } for function in functions]
        payload['parallel_tool_calls'] = False
        choice = chat_request.get('tool_choice', chat_request.get('function_call', 'auto'))
        if isinstance(choice, dict):
            if 'function' in choice:
                choice = {'type': 'function', 'name': choice['function']['name']}
            elif 'name' in choice:
                choice = {'type': 'function', 'name': choice['name']}
        payload['tool_choice'] = choice
    return payload


def _chat_completion(response, legacy_functions):
    output = response.get('output', [])
    text = ''.join(
        part.get('text', '')
        for item in output if item.get('type') == 'message'
        for part in item.get('content', []) if part.get('type') == 'output_text'
    )
    calls = [item for item in output if item.get('type') == 'function_call']
    message = {'role': 'assistant', 'content': text or None, 'function_call': None, 'tool_calls': None}
    if legacy_functions and calls:
        call = calls[0]
        message['function_call'] = {'name': call['name'], 'arguments': call['arguments']}
    elif calls:
        message['tool_calls'] = [{
            'id': call['call_id'],
            'type': 'function',
            'function': {'name': call['name'], 'arguments': call['arguments']},
        } for call in calls]
    usage = response.get('usage') or {}
    return {
        'id': response.get('id', ''),
        'object': 'chat.completion',
        'created': int(response.get('created_at') or time.time()),
        'model': response.get('model', 'gpt-6-luna'),
        'choices': [{
            'index': 0,
            'message': message,
            'finish_reason': 'function_call' if legacy_functions and calls else 'tool_calls' if calls else 'stop',
        }],
        'usage': {
            'prompt_tokens': usage.get('input_tokens', 0),
            'completion_tokens': usage.get('output_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
        },
    }


class JusPrinResponsesTransport(httpx.BaseTransport):
    """Translate the existing JusPrin Chat calls to GPT-6 Luna Responses."""

    def __init__(self, delegate=None):
        self.delegate = delegate or httpx.HTTPTransport()

    def handle_request(self, request):
        if not request.url.path.endswith('/chat/completions'):
            return self.delegate.handle_request(request)
        chat_request = json.loads(request.content)
        payload = _responses_request(chat_request)
        url = request.url.copy_with(path=request.url.path.removesuffix('/chat/completions') + '/responses')
        headers = request.headers.copy()
        headers.pop('content-length', None)
        upstream_request = httpx.Request(
            'POST', url, headers=headers,
            content=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            extensions=request.extensions,
        )
        upstream = self.delegate.handle_request(upstream_request)
        body = upstream.read()
        if upstream.status_code >= 400:
            return httpx.Response(upstream.status_code, content=body,
                                  headers={'content-type': 'application/json'}, request=request)
        response_data = json.loads(body)
        if response_data.get('status') not in (None, 'completed'):
            reason = (response_data.get('incomplete_details') or {}).get('reason') or response_data.get('status')
            return httpx.Response(502, json={
                'error': {'message': f"JusPrin Responses request {response_data['status']}: {reason}"}
            }, request=request)
        converted = _chat_completion(response_data, bool(chat_request.get('functions')))
        return httpx.Response(200, json=converted, request=request)

    def close(self):
        self.delegate.close()


def create_jusprin_client(api_key, base_url, model):
    """Use the benchmarked Responses path for Luna; retain GPT-4o's current path."""
    if model == 'gpt-6-luna':
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=90,
            http_client=httpx.Client(transport=JusPrinResponsesTransport()),
        )
    return OpenAI(api_key=api_key, base_url=base_url)
