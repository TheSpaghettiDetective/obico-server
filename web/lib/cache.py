from django.conf import settings
from django.utils.timezone import now
import redis
import bson
import json
from typing import Optional

REDIS = redis.Redis.from_url(
    settings.REDIS_URL, charset="utf-8", decode_responses=True)

# for binary messages, decoding must be omitted
BREDIS = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)

# redis key prefix
TUNNEL_PREFIX = "octoprinttunnel"

# max wait time for response from plugin
TUNNEL_RSP_TIMEOUT_SECS = 55  # Nginx in production has gateway timeout = 60s. Needs to be shorter than that

# drop unconsumed response from redis after this seconds
TUNNEL_RSP_EXPIRE_SECS = 60

# sent/received stats expiration
TUNNEL_STATS_EXPIRE_SECS = 3600 * 24 * 30 * 6

# etag cache expiration
TUNNEL_ETAG_EXPIRE_SECS = 3600 * 24 * 3


def printer_key_prefix(printer_id):
    return 'printer:{}:'.format(printer_id)


def print_key_prefix(print_id):
    return 'print:{}:'.format(print_id)


def printer_status_set(printer_id, mapping, ex):
    if isinstance(mapping, dict):
        cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}
        prefix = printer_key_prefix(printer_id) + 'status'
        REDIS.hmset(prefix, cleaned_mapping)
        REDIS.expire(prefix, ex)
    else:
        prefix = printer_key_prefix(printer_id) + 'status_str'
        REDIS.setex(prefix, ex, mapping)


def printer_status_get(printer_id, key=None):
    prefix = printer_key_prefix(printer_id) + 'status_str'
    status = REDIS.get(prefix)
    if status:
        results = json.loads(status)
        if key:
            return results.get(key)
        else:
            return results

    prefix = printer_key_prefix(printer_id) + 'status'
    if key:
        v = REDIS.hget(prefix, key)
        if not v:
            return None
        return json.loads(v)
    else:
        status_data = REDIS.hgetall(prefix)
        for k, v in status_data.items():
            status_data[k] = json.loads(v)
        return status_data


def printer_status_delete(printer_id):
    REDIS.delete(printer_key_prefix(printer_id) + 'status_str')
    REDIS.delete(printer_key_prefix(printer_id) + 'status')


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
        # Assuming it'll be processed in 30 days.
        pipe.expire(key, 60*60*24*30)
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
        # Assuming it'll be processed in 3 days.
        pipe.expire(key, 60*60*24*3)
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


def octoprinttunnel_http_response_set(ref, data,
                                      expire_secs=TUNNEL_RSP_EXPIRE_SECS):
    key = f"{TUNNEL_PREFIX}.{ref}"
    with BREDIS.pipeline() as pipe:
        pipe.lpush(key, bson.dumps(data))
        pipe.expire(key, expire_secs)
        pipe.execute()


def octoprinttunnel_http_response_get(ref, timeout_secs=TUNNEL_RSP_TIMEOUT_SECS):
    # no way to delete key in after blpop in a pipeline as
    # blpop does not block in that case..
    key = f"{TUNNEL_PREFIX}.{ref}"
    ret = BREDIS.blpop(key, timeout=timeout_secs)
    if ret is not None and ret[1] is not None:
        BREDIS.delete(key)
        return bson.loads(ret[1])
    return None


def octoprinttunnel_stats_key(date):
    dt = date.strftime('%Y%m')
    return f'{TUNNEL_PREFIX}.stats.{dt}'


def octoprinttunnel_update_stats(user_id, delta):
    key = octoprinttunnel_stats_key(now())
    with REDIS.pipeline() as pipe:
        pipe.hincrby(key, str(user_id), int(delta))
        pipe.expire(key, TUNNEL_STATS_EXPIRE_SECS)
        pipe.execute()


def octoprinttunnel_get_stats(user_id):
    key = octoprinttunnel_stats_key(now())
    return int(REDIS.hget(key, str(user_id)) or '0')


def octoprinttunnel_etag_key(printer_id: int, path: str) -> str:
    return f'{TUNNEL_PREFIX}.etags.{printer_id}.{path}'


def octoprinttunnel_get_etag(printer_id: int, path: str) -> Optional[str]:
    key = octoprinttunnel_etag_key(printer_id, path)
    return REDIS.get(key) or None


def octoprinttunnel_update_etag(printer_id: int, path: str, etag: str) -> None:
    key = octoprinttunnel_etag_key(printer_id, path)
    REDIS.setex(key, TUNNEL_ETAG_EXPIRE_SECS, etag)


def print_status_mobile_push_set(print_id, mobile_platform, ex):
    REDIS.set(f'{print_key_prefix(print_id)}:psmp:{mobile_platform}', 'pushed', ex=ex)

def print_status_mobile_push_get(print_id, mobile_platform):
    return REDIS.get(f'{print_key_prefix(print_id)}:psmp:{mobile_platform}')
