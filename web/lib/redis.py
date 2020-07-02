from django.conf import settings
import redis

REDIS = redis.Redis.from_url(settings.REDIS_URL, charset="utf-8", decode_responses=True)


def printer_key_prefix(printer_id):
    return 'printer:{}:'.format(printer_id)


def print_key_prefix(print_id):
    return 'print:{}:'.format(print_id)


def printer_status_set(printer_id, mapping, ex=None):
    cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}
    prefix = printer_key_prefix(printer_id) + 'status'
    REDIS.hmset(prefix, cleaned_mapping)
    if ex:
        REDIS.expire(prefix, ex)


def printer_status_get(printer_id, key=None):
    prefix = printer_key_prefix(printer_id) + 'status'
    if key:
        return REDIS.hget(prefix, key)
    else:
        return REDIS.hgetall(prefix)


def printer_status_delete(printer_id):
    return REDIS.delete(printer_key_prefix(printer_id) + 'status')


def printer_pic_set(printer_id, mapping, ex=None):
    cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}
    prefix = printer_key_prefix(printer_id) + 'pic'
    REDIS.hmset(prefix, cleaned_mapping)
    if ex:
        REDIS.expire(prefix, ex)


def printer_pic_get(printer_id, key=None):
    prefix = printer_key_prefix(printer_id) + 'pic'
    if key:
        return REDIS.hget(prefix, key)
    else:
        return REDIS.hgetall(prefix)


def printer_settings_set(printer_id, mapping, ex=None):
    cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}
    prefix = printer_key_prefix(printer_id) + 'settings'
    REDIS.hmset(prefix, cleaned_mapping)
    if ex:
        REDIS.expire(prefix, ex)


def printer_settings_get(printer_id, key=None):
    prefix = printer_key_prefix(printer_id) + 'settings'
    if key:
        return REDIS.hget(prefix, key)
    else:
        return REDIS.hgetall(prefix)


def print_num_predictions_incr(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    with REDIS.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, 60*60*24*30)     # Assuming it'll be processed in 30 days.
        pipe.execute()


def print_num_predictions_get(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    return int(REDIS.get(key) or 0)


def print_num_predictions_delete(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    return REDIS.delete(key)


def print_high_prediction_add(print_id, prediction, timestamp, maxsize=180):

    key = f'{print_key_prefix(print_id)}:hp'
    with REDIS.pipeline() as pipe:
        pipe.zadd(key, {timestamp: prediction})
        pipe.zremrangebyrank(key, 0, (-1*maxsize+1))
        pipe.expire(key, 60*60*24*3)     # Assuming it'll be processed in 3 days.
        pipe.execute()


def print_highest_predictions_get(print_id):
    key = f'{print_key_prefix(print_id)}:hp'
    return REDIS.zrevrange(key, 0, -1, withscores=True)


def print_progress_set(print_id, progress_percent):
    key = f'{print_key_prefix(print_id)}:pct'
    REDIS.set(key, str(progress_percent), ex=60*60*24*2)


def print_progress_get(print_id):
    key = f'{print_key_prefix(print_id)}:pct'
    return int(REDIS.get(key) or 0)

