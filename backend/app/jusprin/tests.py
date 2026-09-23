from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import JusPrinPlateAnalysisViewSet
from .plate_analysis_llm_module.analyse_plate_step import (
    is_analyse_plate_prerequisites_not_met,
    is_valid_image_data_url,
)


class PlateAnalysisImageTestCase(SimpleTestCase):
    def test_header_only_image_is_rejected(self):
        chat = {
            'images': ['data:image/jpeg;base64,'] * 4,
            'plates': [{'model_objects': [{'id': '785'}]}],
        }

        self.assertEqual(
            is_analyse_plate_prerequisites_not_met(chat),
            'No images found for analysis. Please contact support.',
        )

    def test_malformed_image_is_rejected(self):
        self.assertFalse(is_valid_image_data_url('data:image/jpeg;base64,not base64'))

    def test_valid_image_data_url_is_accepted(self):
        self.assertTrue(is_valid_image_data_url('data:image/jpeg;base64,/9j/'))


class PlateAnalysisCreditTestCase(SimpleTestCase):
    def post_plate(self, images):
        request = APIRequestFactory().post(
            '/jusprin/api/plate_analysis/',
            {
                'images': images,
                'plates': [{'model_objects': [{'id': '785'}]}],
                'chat_id': 123,
            },
            format='json',
        )
        force_authenticate(request, user=SimpleNamespace(id=1, is_authenticated=True))
        return JusPrinPlateAnalysisViewSet.as_view({'post': 'create'})(request)

    @patch('app.jusprin.views.OpenAI')
    @patch('app.jusprin.views.consume_credit_for_pipeline')
    def test_empty_image_does_not_consume_credit_or_call_openai(self, consume_credit, openai):
        response = self.post_plate(['data:image/jpeg;base64,'] * 4)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message']['role'], 'assistant')
        consume_credit.assert_not_called()
        openai.assert_not_called()

    @patch('app.jusprin.views.analyse_plate_step', return_value={'message': {'role': 'assistant', 'content': 'ok'}})
    @patch('app.jusprin.views.propagate_attributes', return_value=nullcontext())
    @patch('app.jusprin.views.get_client')
    @patch('app.jusprin.views.OpenAI')
    @patch('app.jusprin.views.consume_credit_for_pipeline', return_value={'success': True})
    def test_valid_image_consumes_one_credit(self, consume_credit, openai, get_client,
                                              propagate_attributes, analyse_plate):
        response = self.post_plate(['data:image/jpeg;base64,/9j/'])

        self.assertEqual(response.status_code, 201)
        consume_credit.assert_called_once_with(1)
        openai.assert_called_once()
        analyse_plate.assert_called_once()
