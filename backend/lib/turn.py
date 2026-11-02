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


def get_turn_config(printer, ttl_seconds=None):
    """
    TURN info for a printer, in the same contract shape the agents receive as
    `printer.turn` from /api/v1/octo/printer/.

    Credentials are issued per printer, mirroring the per-printer auth tokens: a printer's agent,
    its owner's browser and mobile app, and shared-page viewers all get credentials minted for
    that printer. None when no TURN server is configured.

    Defaults to the web TTL; callers such as the agent API can ask for their own.
    """
    ttl = settings.TURN_WEB_CREDENTIAL_TTL if ttl_seconds is None else ttl_seconds
    return turn_config(label=f'printer-{printer.id}', ttl_seconds=ttl)
