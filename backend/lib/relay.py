# The video relay settings a client gets from the server: WebRTC ice servers
# (STUN, then the relay with a short-lived credential). See RELAY_* in
# config/settings.py. The credential is coturn's use-auth-secret scheme:
# username "<expiry unix time>:<name>", password base64(HMAC-SHA1(secret,
# username)). The relay refuses it after the expiry.
import base64
import hashlib
import hmac
import time

from django.conf import settings


def credential_password(username, secret):
    return base64.b64encode(hmac.new(secret.encode(), username.encode(), hashlib.sha1).digest()).decode()


STUN_URLS = ['stun:stun.l.google.com:19302']


def viewer_urls(host):
    # Browsers and apps can reach the relay over TLS.
    return [f'turns:{host}:443?transport=tcp', f'turn:{host}:80?transport=udp']


def printer_urls(host):
    # Janus on a printer takes one relay, and its libnice never encrypts the
    # connection, so plain TCP.
    return [f'turn:{host}:80?transport=tcp']


def _ice_servers(urls_for_host, name, lifetime_secs):
    servers = [{'urls': STUN_URLS}]
    expires_at = None
    if settings.RELAY_HOST:
        expires_at = int(time.time()) + lifetime_secs
        username = f'{expires_at}:{name}'
        servers.append({
            'urls': urls_for_host(settings.RELAY_HOST),
            'username': username,
            'credential': credential_password(username, settings.RELAY_SECRETS[0]),
        })
    return {'ice_servers': servers, 'expires_at': expires_at}


# The relay limits allocations per username, so each printer gets its own
# names: one for the printer itself, one for its owner's viewers, one for
# viewers of its shared link.

def for_printer(printer):
    return _ice_servers(printer_urls, f'p{printer.id}', settings.RELAY_PRINTER_CREDENTIAL_SECS)


def for_viewer(printer):
    return _ice_servers(viewer_urls, f'v{printer.id}', settings.RELAY_VIEWER_CREDENTIAL_SECS)


def for_shared_viewer(printer):
    return _ice_servers(viewer_urls, f's{printer.id}', settings.RELAY_VIEWER_CREDENTIAL_SECS)
