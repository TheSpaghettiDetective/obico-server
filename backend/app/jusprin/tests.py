from django.test import SimpleTestCase

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
