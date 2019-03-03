from django.conf import settings
import redis

REDIS = redis.Redis.from_url(settings.REDIS_URL, charset="utf-8", decode_responses=True)


def printer_key_prefix(printer_id):
    return 'printer:{}:'.format(printer_id)

def printer_status_set(printer_id, mapping, ex=None):
    cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}
    prefix = printer_key_prefix(printer_id) + 'status'
    REDIS.hmset(prefix, cleaned_mapping)
    if ex:
        REDIS.expire(prefix, ex)

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

def printer_status_get(printer_id, key=None):
    prefix = printer_key_prefix(printer_id) + 'status'
    if key:
        return REDIS.hget(prefix, key)
    else:
        return REDIS.hgetall(prefix)

def printer_status_delete(printer_id, key):
    return REDIS.hdel(printer_key_prefix(printer_id) + 'status', key)
