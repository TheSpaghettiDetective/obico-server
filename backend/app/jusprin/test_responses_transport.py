"""Contract checks for JusPrin's Responses API boundary."""

import json
import unittest

import httpx

from app.jusprin.responses_transport import JusPrinResponsesTransport


class StubTransport(httpx.BaseTransport):
    def __init__(self, status=200, output=None):
        self.status = status
        self.output = output if output is not None else [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'Ready'}]}]
        self.request = None

    def handle_request(self, request):
        self.request = request
        if self.status >= 400:
            return httpx.Response(self.status, json={'error': {'message': 'Rejected'}}, request=request)
        return httpx.Response(200, json={
            'id': 'resp_test', 'model': 'gpt-6-luna', 'created_at': 1,
            'output': self.output,
            'usage': {'input_tokens': 11, 'output_tokens': 7, 'total_tokens': 18},
        }, request=request)


class JusPrinResponsesTransportTest(unittest.TestCase):
    def send(self, chat_body, upstream=None):
        upstream = upstream or StubTransport()
        transport = JusPrinResponsesTransport(delegate=upstream)
        request = httpx.Request('POST', 'https://api.openai.com/v1/chat/completions', json=chat_body)
        return transport.handle_request(request), upstream

    def test_text_and_usage(self):
        response, upstream = self.send({
            'model': 'gpt-6-luna', 'messages': [{'role': 'user', 'content': 'Hello'}], 'temperature': 0,
        })
        payload = json.loads(upstream.request.content)
        self.assertEqual(upstream.request.url.path, '/v1/responses')
        self.assertEqual(payload['reasoning'], {'effort': 'low'})
        self.assertIs(payload['store'], False)
        self.assertNotIn('temperature', payload)
        self.assertEqual(response.json()['choices'][0]['message']['content'], 'Ready')
        self.assertEqual(response.json()['usage']['total_tokens'], 18)

    def test_function_call_and_multiturn_output(self):
        upstream = StubTransport(output=[{
            'type': 'function_call', 'call_id': 'call_1', 'name': 'slice_model', 'arguments': '{}',
        }])
        response, upstream = self.send({
            'model': 'gpt-6-luna',
            'messages': [
                {'role': 'user', 'content': 'Slice'},
                {'role': 'assistant', 'tool_calls': [{
                    'id': 'call_0', 'type': 'function',
                    'function': {'name': 'inspect', 'arguments': '{}'},
                }]},
                {'role': 'tool', 'tool_call_id': 'call_0', 'content': 'done'},
            ],
            'functions': [{'name': 'slice_model', 'parameters': {'type': 'object', 'properties': {}}}],
            'function_call': 'auto',
        }, upstream)
        payload = json.loads(upstream.request.content)
        self.assertEqual(payload['input'][1]['type'], 'function_call')
        self.assertEqual(payload['input'][2]['call_id'], 'call_0')
        self.assertEqual(payload['tools'][0]['name'], 'slice_model')
        self.assertIs(payload['parallel_tool_calls'], False)
        self.assertEqual(response.json()['choices'][0]['message']['function_call']['name'], 'slice_model')

    def test_plate_image_and_error_passthrough(self):
        response, upstream = self.send({
            'model': 'gpt-6-luna',
            'messages': [{'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,AA=='}}]}],
        })
        self.assertEqual(json.loads(upstream.request.content)['input'][0]['content'][0]['type'], 'input_image')
        self.assertEqual(response.status_code, 200)
        error, _ = self.send({'model': 'gpt-6-luna', 'messages': []}, StubTransport(status=429))
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.json()['error']['message'], 'Rejected')

    def test_incomplete_response_is_not_silently_accepted(self):
        class IncompleteTransport(httpx.BaseTransport):
            def handle_request(self, request):
                return httpx.Response(200, json={
                    'status': 'incomplete', 'output': [],
                    'incomplete_details': {'reason': 'max_output_tokens'},
                }, request=request)

        response, _ = self.send({'model': 'gpt-6-luna', 'messages': []}, IncompleteTransport())
        self.assertEqual(response.status_code, 502)


if __name__ == '__main__':
    unittest.main()
