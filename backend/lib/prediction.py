"""
Failure Detection Prediction Algorithm.

Provides functions for updating prediction state and determining if a print is failing.
Both 1st gen and 2nd gen detection use these functions with different hyperparameters.
"""

import logging

LOGGER = logging.getLogger(__name__)


def update_prediction_with_detections(prediction, detections, params, bending_factor=None):
    """
    Update prediction with new detections.

    Args:
        prediction: PrinterPrediction model instance
        detections: list of [label, confidence, box] pairs
        params: dict with EWM_SPAN, ROLLING_WIN_SHORT, ROLLING_WIN_LONG, MAX_DET_NUM (optional)
        bending_factor: optional multiplier for confidence scores
    """
    if bending_factor is not None:
        for d in detections:
            d[1] = d[1] * bending_factor

    max_det_num = params.get('MAX_DET_NUM')
    if max_det_num:
        detections = sorted(detections, key=lambda d: d[1], reverse=True)[:max_det_num]

    p = sum_p_in_detections(detections)
    ewm_alpha = 2 / (params['EWM_SPAN'] + 1)

    prediction.current_p = p
    prediction.current_frame_num += 1
    prediction.lifetime_frame_num += 1
    prediction.ewm_mean = next_ewm_mean(p, prediction.ewm_mean, ewm_alpha)
    prediction.rolling_mean_short = next_rolling_mean(
        p, prediction.rolling_mean_short,
        prediction.current_frame_num, params['ROLLING_WIN_SHORT']
    )
    prediction.rolling_mean_long = next_rolling_mean(
        p, prediction.rolling_mean_long,
        prediction.lifetime_frame_num, params['ROLLING_WIN_LONG']
    )


def is_failing(prediction, detective_sensitivity, params, escalating_factor=1):
    """
    Determine if print is failing based on prediction state.

    Args:
        prediction: PrinterPrediction model instance
        detective_sensitivity: user's sensitivity setting (multiplier)
        params: dict with THRESHOLD_LOW, THRESHOLD_HIGH, INIT_SAFE_FRAME_NUM, ROLLING_MEAN_SHORT_MULTIPLE
        escalating_factor: divisor for escalation (use params['ESCALATING_FACTOR'] for pause decision)

    Returns:
        bool: True if print appears to be failing
    """
    if prediction.current_frame_num < params['INIT_SAFE_FRAME_NUM']:
        return False

    adjusted_ewm_mean = (prediction.ewm_mean - prediction.rolling_mean_long) * detective_sensitivity / escalating_factor

    if adjusted_ewm_mean < params['THRESHOLD_LOW']:
        return False

    if adjusted_ewm_mean > params['THRESHOLD_HIGH']:
        return True

    if adjusted_ewm_mean > (prediction.rolling_mean_short - prediction.rolling_mean_long) * params['ROLLING_MEAN_SHORT_MULTIPLE']:
        return True

    return False


def next_ewm_mean(p, current_ewm_mean, alpha):
    """Calculate next exponential weighted mean."""
    return p * alpha + current_ewm_mean * (1 - alpha)


def next_rolling_mean(p, current_rolling_mean, count, win_size):
    """
    Calculate next rolling mean approximation.
    Inspired by https://dev.to/nestedsoftware/calculating-a-moving-average-on-streaming-data-5a7k
    """
    return current_rolling_mean + (p - current_rolling_mean) / float(
        win_size if win_size <= count else count + 1
    )


def sum_p_in_detections(detections):
    """Sum confidence scores from detections."""
    return sum(d[1] for d in detections)
