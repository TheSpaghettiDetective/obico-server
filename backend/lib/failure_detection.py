"""Failure detection module - extracted from octoprint_views.py"""

import io
import json
import logging
import requests
from django.conf import settings
from django.core import serializers
from PIL import Image

from lib.file_storage import save_file_obj
from lib import cache
from lib.image import overlay_detections
from lib.utils import ml_api_auth_headers
from lib.prediction import update_prediction_with_detections, is_failing
from app.models import PrinterPrediction

LOGGER = logging.getLogger(__name__)

IMG_URL_TTL_SECONDS = 60 * 30


def calc_normalized_p(detective_sensitivity: float,
                      pred: 'PrinterPrediction',
                      params: dict) -> float:
    """Calculate normalized prediction value (0-1 scale) for UI display."""
    def scale(oldValue, oldMin, oldMax, newMin, newMax):
        newValue = (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin
        return min(newMax, max(newMin, newValue))
    thresh_warning = (pred.rolling_mean_short - pred.rolling_mean_long) * params['ROLLING_MEAN_SHORT_MULTIPLE']
    thresh_warning = min(params['THRESHOLD_HIGH'], max(params['THRESHOLD_LOW'], thresh_warning))
    thresh_failure = thresh_warning * params['ESCALATING_FACTOR']

    p = (pred.ewm_mean - pred.rolling_mean_long) * detective_sensitivity

    if p > thresh_failure:
        return scale(p, thresh_failure, thresh_failure * 1.5, 2.0 / 3.0, 1.0)
    elif p > thresh_warning:
        return scale(p, thresh_warning, thresh_failure, 1.0 / 3.0, 2.0 / 3.0)
    else:
        return scale(p, 0, thresh_warning, 0, 1.0 / 3.0)


def detect(printer, pic, pic_id, raw_pic_url, ml_api_endpoint, params):
    """
    Perform failure detection. Returns dict with 'detections', 'decision', 'tagged_img_url'.
    """

    prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)

    req = requests.get(settings.ML_API_HOST + ml_api_endpoint, params={'img': raw_pic_url}, headers=ml_api_auth_headers(), verify=False)
    req.raise_for_status()
    detections = req.json()['detections']

    if settings.DEBUG:
        LOGGER.info(f'Detections: {detections}')

    update_prediction_with_detections(prediction, detections, params, bending_factor=printer.detection_bending_factor)
    prediction.normalized_p = calc_normalized_p(printer.detective_sensitivity, prediction, params)
    prediction.save()

    if prediction.current_p > params['THRESHOLD_LOW'] * 0.2:
        cache.print_high_prediction_add(printer.current_print.id, prediction.current_p, pic_id)

    pic.file.seek(0)
    tagged_img = io.BytesIO()
    detections_to_visualize = [d for d in detections if d[1] > params['VISUALIZATION_THRESH']]
    overlay_detections(Image.open(pic.file), detections_to_visualize).save(tagged_img, "JPEG")
    tagged_img.seek(0)

    pic_path = f'tagged/{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
    _, tagged_img_url = save_file_obj(pic_path, tagged_img, settings.PICS_CONTAINER, printer.user.syndicate.name, long_term_storage=False)
    cache.printer_pic_set(printer.id, {'img_url': tagged_img_url}, ex=IMG_URL_TTL_SECONDS)

    prediction_json = serializers.serialize("json", [prediction, ])
    p_out = io.BytesIO()
    p_out.write(prediction_json.encode('UTF-8'))
    p_out.seek(0)
    save_file_obj(f'p/{printer.id}/{printer.current_print.id}/{pic_id}.json', p_out, settings.PICS_CONTAINER, printer.user.syndicate.name, long_term_storage=False)

    should_pause = is_failing(prediction, printer.detective_sensitivity, params, escalating_factor=params['ESCALATING_FACTOR'])
    should_alert = not should_pause and is_failing(prediction, printer.detective_sensitivity, params, escalating_factor=1)

    return {
        'detections': detections,
        'decision': {'should_pause': should_pause, 'should_alert': should_alert},
        'tagged_img_url': tagged_img_url,
    }
