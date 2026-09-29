import base64
import hashlib
import hmac
import time

from django.conf import settings


def turn_config(label, ttl_seconds):
    """
    TURN configuration for a WebRTC client, or None when no TURN server is configured.

    In shared-secret mode a time-limited credential is issued as specified by the TURN REST API
    (draft-uberti-behave-turn-rest): the username is "<expiry>:<label>" and the credential is the
    base64 HMAC-SHA1 of the username, keyed with the shared secret. In static mode the configured
    username and credential are returned as-is and never expire.
    """
    if not settings.TURN_SERVER:
        return None

    if settings.TURN_SECRET:
        expires_at = int(time.time()) + int(ttl_seconds)
        username = f'{expires_at}:{label}'
        digest = hmac.new(settings.TURN_SECRET.encode(), username.encode(), hashlib.sha1).digest()
        credential = base64.b64encode(digest).decode()
    else:
        expires_at = None
        username = settings.TURN_USERNAME
        credential = settings.TURN_CREDENTIAL

    return {
        'server': settings.TURN_SERVER,
        'port': settings.TURN_PORT,
        'transports': list(settings.TURN_TRANSPORTS),
        'username': username,
        'credential': credential,
        'expires_at': expires_at,
    }
