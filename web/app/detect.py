
EWMA_ALPHA = 0.4

def next_score(current_score, detections):
    if not current_score:
        current_score = 0

    sum_score = sum([ d[1] for d in detections ])
    return sum_score * EWMA_ALPHA + current_score * (1-EWMA_ALPHA)

