"""
Failure Detection Prediction Algorithm.

Provides functions for updating prediction state and determining if a print is failing.
Both 1st gen and 2nd gen detection use these functions with different hyperparameters.
"""

import logging

LOGGER = logging.getLogger(__name__)


def update_prediction_with_detections(prediction_state, detections, params, bending_factor=None):
    """
    Update prediction state with new detections.

    Args:
        prediction_state: dict with current_p, ewm_mean, rolling_mean_short, etc.
                         Can also be a PrinterPrediction model instance.
        detections: list of [label, confidence, box] or [box, confidence] pairs
        params: dict with EWM_SPAN, ROLLING_WIN_SHORT, ROLLING_WIN_LONG
        bending_factor: optional multiplier for confidence scores (from printer settings)

    Returns:
        dict: Updated prediction state (or modifies model in place if passed a model)
    """
    # Handle both dict and model object
    is_model = hasattr(prediction_state, 'save')

    if is_model:
        state = {
            'current_p': prediction_state.current_p,
            'current_frame_num': prediction_state.current_frame_num,
            'lifetime_frame_num': prediction_state.lifetime_frame_num,
            'ewm_mean': prediction_state.ewm_mean,
            'rolling_mean_short': prediction_state.rolling_mean_short,
            'rolling_mean_long': prediction_state.rolling_mean_long,
        }
    else:
        state = prediction_state

    # Apply bending factor if set
    if bending_factor is not None:
        for d in detections:
            d[1] = d[1] * bending_factor

    # Apply MAX_DET_NUM if specified (used by 2nd gen)
    max_det_num = params.get('MAX_DET_NUM')
    if max_det_num:
        detections = sorted(detections, key=lambda d: d[1], reverse=True)[:max_det_num]

    p = sum_p_in_detections(detections)
    ewm_alpha = 2 / (params['EWM_SPAN'] + 1)

    state['current_p'] = p
    state['current_frame_num'] = state.get('current_frame_num', 0) + 1
    state['lifetime_frame_num'] = state.get('lifetime_frame_num', 0) + 1
    state['ewm_mean'] = next_ewm_mean(p, state.get('ewm_mean', 0), ewm_alpha)
    state['rolling_mean_short'] = next_rolling_mean(
        p, state.get('rolling_mean_short', 0),
        state['current_frame_num'], params['ROLLING_WIN_SHORT']
    )
    state['rolling_mean_long'] = next_rolling_mean(
        p, state.get('rolling_mean_long', 0),
        state['lifetime_frame_num'], params['ROLLING_WIN_LONG']
    )

    # If passed a model, update it in place
    if is_model:
        prediction_state.current_p = state['current_p']
        prediction_state.current_frame_num = state['current_frame_num']
        prediction_state.lifetime_frame_num = state['lifetime_frame_num']
        prediction_state.ewm_mean = state['ewm_mean']
        prediction_state.rolling_mean_short = state['rolling_mean_short']
        prediction_state.rolling_mean_long = state['rolling_mean_long']
        return prediction_state

    return state


def is_failing(prediction_state, detective_sensitivity, params, escalating_factor=1):
    """
    Determine if print is failing based on prediction state.

    Args:
        prediction_state: dict with ewm_mean, rolling_mean_short, rolling_mean_long, current_frame_num
                         Can also be a PrinterPrediction model instance.
        detective_sensitivity: user's sensitivity setting (multiplier)
        params: dict with THRESHOLD_LOW, THRESHOLD_HIGH, INIT_SAFE_FRAME_NUM, ROLLING_MEAN_SHORT_MULTIPLE
        escalating_factor: divisor for escalation (use params['ESCALATING_FACTOR'] for pause decision)

    Returns:
        bool: True if print appears to be failing
    """
    # Handle both dict and model object
    if hasattr(prediction_state, 'current_frame_num'):
        # It's a model object
        current_frame_num = prediction_state.current_frame_num
        ewm_mean = prediction_state.ewm_mean
        rolling_mean_short = prediction_state.rolling_mean_short
        rolling_mean_long = prediction_state.rolling_mean_long
    else:
        # It's a dict
        current_frame_num = prediction_state.get('current_frame_num', 0)
        ewm_mean = prediction_state.get('ewm_mean', 0)
        rolling_mean_short = prediction_state.get('rolling_mean_short', 0)
        rolling_mean_long = prediction_state.get('rolling_mean_long', 0)

    if current_frame_num < params['INIT_SAFE_FRAME_NUM']:
        return False

    adjusted_ewm_mean = (ewm_mean - rolling_mean_long) * detective_sensitivity / escalating_factor

    if adjusted_ewm_mean < params['THRESHOLD_LOW']:
        return False

    if adjusted_ewm_mean > params['THRESHOLD_HIGH']:
        return True

    if adjusted_ewm_mean > (rolling_mean_short - rolling_mean_long) * params['ROLLING_MEAN_SHORT_MULTIPLE']:
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
