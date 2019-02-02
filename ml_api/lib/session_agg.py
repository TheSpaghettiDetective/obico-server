EWMA_ALPHA = 2/(20 + 1) # 0.4

def next_ewma(cur_ewma, value):
    return value * EWMA_ALPHA + cur_ewma * (1-EWMA_ALPHA)

def predict(detections, session):
    current_ewma = float(session.get('ewma', '0.0'))
    current_detection_sum = sum([ d[1] for d in detections ])
    ewma = next_ewma(current_ewma, current_detection_sum)

    return ewma, {'ewma': ewma}
