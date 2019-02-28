EWM_ALPHA = 2/(20 + 1)
ROLLING_WIN_SHORT = 80 # rolling window of 80 samples
ROLLING_WIN_LONG = 10000 # rolling window of 10000 samples. Approximation of printer's base noise level

THRESHOLD_LOW = 0.15   # Definitely not failing if ewm mean is below this level
THRESHOLD_HIGH = 0.55    # Definitely failing if ewm mean is above this level
ROLLING_SHORT_MULTIPLE = 5.5   # Print is failing is ewm mean is this many times over the short rolling mean
INIT_SAFE_FRAME_NUM = 30        # The number of frames at the beginning of the print that are considered "safe"

def update_prediction_with_detections(prediction, detections):
    p = sum_p_in_detections(detections)
    prediction.current_p = p
    prediction.current_frame_num += 1
    prediction.ewm_mean = next_ewm_mean(p, prediction.ewm_mean)
    prediction.rolling_mean_short = next_rolling_mean_short(p, prediction.rolling_mean_short)
    prediction.rolling_mean_long = next_rolling_mean_long(p, prediction.rolling_mean_long)

def is_failing(prediction):
    if prediction.current_frame_num < INIT_SAFE_FRAME_NUM:
        return False

    if prediction.ewm_mean < THRESHOLD_LOW + prediction.rolling_mean_long:
        return False

    if prediction.ewm_mean > THRESHOLD_HIGH + prediction.rolling_mean_long:
        return True

    if prediction.ewm_mean > prediction.rolling_mean_short * ROLLING_SHORT_MULTIPLE:
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
