from django.conf import settings

def printer_key_prefix(printer_id):
    return 'printer:{}:'.format(printer_id)

def printer_status_set(printer_id, mapping, ex=None):
    cleaned_mapping = {k: v for k, v in mapping.items() if v is not None}

    r = settings.REDIS_CONN
    prefix = printer_key_prefix(printer_id) + 'status'
    r.hmset(prefix, cleaned_mapping)
    if ex:
        r.expire(prefix, ex)

def printer_pic_set(printer_id, key, value, ex=None):
    r = settings.REDIS_CONN
    prefix = printer_key_prefix(printer_id) + 'pic'
    r.hset(prefix, key, value)
    if ex:
        r.expire(prefix, ex)

def printer_pic_get(printer_id, key=None):
    r = settings.REDIS_CONN
    prefix = printer_key_prefix(printer_id) + 'pic'
    if key:
        return r.hget(prefix, key)
    else:
        return r.hgetall(prefix)

def printer_status_get(printer_id, key=None):
    r = settings.REDIS_CONN
    prefix = printer_key_prefix(printer_id) + 'status'
    if key:
        return r.hget(prefix, key)
    else:
        return r.hgetall(prefix)

def printer_status_delete(printer_id, key):
    r = settings.REDIS_CONN
    return r.hdel(printer_key_prefix(printer_id) + 'status', key)
