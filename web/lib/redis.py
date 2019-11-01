from django.conf import settings
import redis

REDIS = redis.Redis.from_url(settings.REDIS_URL, charset="utf-8", decode_responses=True)


def printer_key_prefix(printer_id):
    return 'printer:{}:'.format(printer_id)

def user_key_prefix(user_id):
    return 'user:{}:'.format(user_id)

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

def printer_status_delete(printer_id, key):
    return REDIS.hdel(printer_key_prefix(printer_id) + 'status', key)

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

def printer_p_json_set(printer_id, pic_id, json_str, ex=None):
    key = f'{printer_key_prefix(printer_id)}:p_json:{pic_id}'
    REDIS.set(key, json_str, ex=ex)

def printer_p_json_get(printer_id, pic_id):
    key = f'{printer_key_prefix(printer_id)}:p_json:{pic_id}'
    return REDIS.get(key)

def user_dh_balance_set(user_id, balance):
    key = f'{user_key_prefix(user_id)}:dh'
    REDIS.set(key, balance)

def user_dh_balance_get(user_id):
    key = f'{user_key_prefix(user_id)}:dh'
    return float(REDIS.get(key) or 0)

def print_num_predictions_incr(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    with REDIS.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, 60*60*24*5)     # Assuming it'll be processed in 5 days.
        pipe.execute()

def print_num_predictions_get(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    return int(REDIS.get(key) or 0)

def print_num_predictions_delete(print_id):
    key = f'{print_key_prefix(print_id)}:pred'
    return REDIS.delete(key)
