from django.conf import settings

EWM_ALPHA = 2/(9 + 1)   # 9 is the optimal EWM span in hyper parameter grid search
ROLLING_WIN_SHORT = 88 # rolling window of 88 samples.
ROLLING_WIN_LONG = 7200 # rolling window of 7200 samples (~20 hours). Approximation of printer's base noise level

ROLLING_MEAN_SHORT_MULTIPLE = 5.43   # Print is failing is ewm mean is this many times over the short rolling mean
INIT_SAFE_FRAME_NUM = 30        # The number of frames at the beginning of the print that are considered "safe"

def update_prediction_with_detections(prediction, detections):
    p = sum_p_in_detections(detections)
    prediction.current_p = p
    prediction.current_frame_num += 1
    prediction.ewm_mean = next_ewm_mean(p, prediction.ewm_mean)
    prediction.rolling_mean_short = next_rolling_mean_short(p, prediction.rolling_mean_short)
    prediction.rolling_mean_long = next_rolling_mean_long(p, prediction.rolling_mean_long)

def is_failing(prediction):
    print(prediction)
    if prediction.current_frame_num < INIT_SAFE_FRAME_NUM:
        return False

    if prediction.ewm_mean < settings.THRESHOLD_LOW + prediction.rolling_mean_long:
        return False

    if prediction.ewm_mean > settings.THRESHOLD_HIGH + prediction.rolling_mean_long:
        return True

    if prediction.ewm_mean > prediction.rolling_mean_short * ROLLING_MEAN_SHORT_MULTIPLE:
        return True

def next_ewm_mean(p, current_ewm_mean):
    return p * EWM_ALPHA + current_ewm_mean * (1-EWM_ALPHA)

def next_rolling_mean_short(p, current_rolling_mean):
    return next_rolling_mean(p, current_rolling_mean, ROLLING_WIN_SHORT)

def next_rolling_mean_long(p, current_rolling_mean):
    return next_rolling_mean(p, current_rolling_mean, ROLLING_WIN_LONG)

# Approximation of rolling mean
def next_rolling_mean(p, current_rolling_mean, win_size):
    return current_rolling_mean + (p - current_rolling_mean )/float(win_size)

def sum_p_in_detections(detections):
    return sum([ d[1] for d in detections ])
