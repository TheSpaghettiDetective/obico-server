import logging
import requests
from django.conf import settings

from lib.utils import ml_api_auth_headers

LOGGER = logging.getLogger(__name__)


def fd_2nd_gen_enabled(user):
    return bool(getattr(user, 'fd_2nd_gen_enabled', False))


def _prediction_state_from_obj(prediction):
    if prediction is None:
        return {
            'prediction_num': 0,
            'prediction_num_lifetime': 0,
            'ewm_mean': 0.0,
            'rolling_mean_short': 0.0,
            'rolling_mean_long': 0.0,
        }

    return {
        'prediction_num': prediction.current_frame_num,
        'prediction_num_lifetime': prediction.lifetime_frame_num,
        'ewm_mean': prediction.ewm_mean,
        'rolling_mean_short': prediction.rolling_mean_short,
        'rolling_mean_long': prediction.rolling_mean_long,
    }


def _printer_context(printer):
    if printer is None:
        return {
            'detective_sensitivity': 1,
            'detection_bending_factor': None,
        }

    return {
        'detective_sensitivity': printer.detective_sensitivity,
        'detection_bending_factor': printer.detection_bending_factor,
    }


def apply_fd_2nd_gen_prediction(prediction, result):
    if prediction is None or not result:
        return

    temporal_stats = result.get('temporal_stats', {})
    prediction.current_p = result.get('p', prediction.current_p)
    prediction.ewm_mean = temporal_stats.get('ewm_mean', prediction.ewm_mean)
    prediction.rolling_mean_short = temporal_stats.get('rolling_mean_short', prediction.rolling_mean_short)
    prediction.rolling_mean_long = temporal_stats.get('rolling_mean_long', prediction.rolling_mean_long)
    prediction.current_frame_num = temporal_stats.get('prediction_num', prediction.current_frame_num)
    prediction.lifetime_frame_num = temporal_stats.get('prediction_num_lifetime', prediction.lifetime_frame_num)


def fd_2nd_gen_predict(img_url, prediction=None, printer=None, return_detections=False):
    if not settings.FD_2ND_GEN_API_URL:
        LOGGER.warning('FD_2ND_GEN_API_URL not configured')
        return None

    payload = {
        'img_url': img_url,
        'prediction_state': _prediction_state_from_obj(prediction),
        'printer_context': _printer_context(printer),
        'return_detections': return_detections,
    }

    try:
        resp = requests.post(
            settings.FD_2ND_GEN_API_URL,
            json=payload,
            headers=ml_api_auth_headers(),
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as err:
        LOGGER.warning('FD 2nd gen prediction failed: %s', err)
        return None
