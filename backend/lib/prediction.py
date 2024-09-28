import logging
from django.conf import settings

LOGGER = logging.getLogger(__name__)

EWM_ALPHA = 2/(12 + 1)   # 12 is the optimal EWM span in hyper parameter grid search
ROLLING_WIN_SHORT = 310 # rolling window of 310 samples.
ROLLING_WIN_LONG = 7200 # rolling window of 7200 samples (~20 hours). Approximation of printer's base noise level

VISUALIZATION_THRESH = 0.2  # The thresh for a box to be drawn on the detective view

def update_prediction_with_detections(prediction, detections, printer):

    if printer and printer.detection_bending_factor is not None: # Bend bend bend
        for d in detections:
            d[1] = d[1] * printer.detection_bending_factor

    p = sum_p_in_detections(detections)
    prediction.current_p = p
    prediction.current_frame_num += 1
    prediction.lifetime_frame_num += 1
    prediction.ewm_mean = next_ewm_mean(p, prediction.ewm_mean)
    prediction.rolling_mean_short = next_rolling_mean(p, prediction.rolling_mean_short, prediction.current_frame_num, ROLLING_WIN_SHORT)
    prediction.rolling_mean_long = next_rolling_mean(p, prediction.rolling_mean_long, prediction.lifetime_frame_num, ROLLING_WIN_LONG)

def is_failing(prediction, detective_sensitivity, escalating_factor=1):
    if prediction.current_frame_num < settings.INIT_SAFE_FRAME_NUM:
        return False

    adjusted_ewm_mean = (prediction.ewm_mean - prediction.rolling_mean_long) * detective_sensitivity / escalating_factor
    if adjusted_ewm_mean < settings.THRESHOLD_LOW:
        return False

    if adjusted_ewm_mean > settings.THRESHOLD_HIGH:
        return True

    if adjusted_ewm_mean > (prediction.rolling_mean_short - prediction.rolling_mean_long) * settings.ROLLING_MEAN_SHORT_MULTIPLE:
        return True

def next_ewm_mean(p, current_ewm_mean):
    return p * EWM_ALPHA + current_ewm_mean * (1-EWM_ALPHA)

# Approximation of rolling mean. inspired by https://dev.to/nestedsoftware/calculating-a-moving-average-on-streaming-data-5a7k
def next_rolling_mean(p, current_rolling_mean, count, win_size):
    return current_rolling_mean + (p - current_rolling_mean )/float(win_size if win_size <= count else count+1)

def sum_p_in_detections(detections):
    return sum([ d[1] for d in detections ])
