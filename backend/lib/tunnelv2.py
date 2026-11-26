from typing import Optional, Union

import logging
import base64
import binascii
import re

# from asgiref.typing import HTTPScope
import django.http
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core import signing
from django.utils.crypto import constant_time_compare
from django.core.exceptions import PermissionDenied
from app.models import User, OctoPrintTunnel

HTTPScope = dict
ScopeOrRequest = Union[HTTPScope, django.http.HttpRequest]

LOGGER = logging.getLogger(__name__)

# Signs a person in to one tunnel on settings.TUNNEL_DOMAIN, where this site's own
# sign-in cookie is not sent. Set by tunnelv2_views.tunnel_signin.
TUNNEL_SESSION_COOKIE_NAME = 'tsd_tunnel_session'
TUNNEL_SESSION_SALT = 'lib.tunnelv2.tunnel_session'
TUNNEL_CODE_RE = re.compile(r'^\w+$')


def tunnel_session_cookie_value(tunnel: OctoPrintTunnel, user: User) -> str:
    # The password hash part makes a password change sign the person out of the tunnel too
    return signing.dumps(
        {'tunnel': tunnel.id, 'user': user.id, 'auth': user.get_session_auth_hash()},
        salt=TUNNEL_SESSION_SALT)


class TunnelAuthenticationError(Exception):

    def __init__(self, message: str, realm: Optional[str], **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.message: str = message
        self.realm: str = realm


class OctoprintTunnelV2Helper(object):

    @classmethod
    def get_host(cls, s_or_r: ScopeOrRequest) -> str:
        if isinstance(s_or_r, django.http.HttpRequest):
            return s_or_r.get_host()

        host = [
            hpair[1]
            for hpair in s_or_r['headers']
            if hpair[0] == b'host'
        ][0]
        return host.decode()

    @classmethod
    def get_port(cls, s_or_r: ScopeOrRequest) -> Optional[int]:
        try:
            return int(cls.get_host(s_or_r).rsplit(':', 1)[1])
        except (ValueError, IndexError):
            return None

    @classmethod
    def get_tunnel_domain_code(cls, s_or_r: ScopeOrRequest) -> Optional[str]:
        # "abc123" for a request to abc123.<settings.TUNNEL_DOMAIN>; None for any other host
        if not settings.TUNNEL_DOMAIN:
            return None
        hostname = cls.get_host(s_or_r).split(':')[0].lower()
        code, _, domain = hostname.partition('.')
        if domain == settings.TUNNEL_DOMAIN.split(':')[0] and TUNNEL_CODE_RE.match(code):
            return code
        return None

    @classmethod
    def is_on_tunnel_domain(cls, tunnel: OctoPrintTunnel) -> bool:
        return bool(settings.TUNNEL_DOMAIN and tunnel.subdomain_code)

    @classmethod
    def get_subdomain_code(cls, s_or_r: ScopeOrRequest) -> str:
        code = cls.get_tunnel_domain_code(s_or_r)
        if code:
            return code

        host = cls.get_host(s_or_r)
        try:
            m = settings.OCTOPRINT_TUNNEL_SUBDOMAIN_RE.match(host)
            if m is not None:
                return m.groups()[0]
        except IndexError:
            return None

    @classmethod
    def get_authorization_header(
        cls, s_or_r: ScopeOrRequest
    ) -> Optional[str]:
        if isinstance(s_or_r, django.http.HttpRequest):
            v = s_or_r.headers.get('Authorization', '').strip()
        else:
            try:
                v = [
                    hpair[1]
                    for hpair in s_or_r['headers']
                    if hpair[0] == b'authorization'
                ][0].decode()
            except IndexError:
                v = ''

        for authorization in v.split(','):
            try:
                token_name, token_key = authorization.split()
            except ValueError:
                continue

            if token_name.lower() == 'basic':
                return authorization

        return ''

    @classmethod
    def _get_user(cls, s_or_r: ScopeOrRequest) -> Optional[User]:
        if isinstance(s_or_r, django.http.HttpRequest):
            # Not "'user' in s_or_r": on a request, "in" reads through its body
            return s_or_r.user if s_or_r.user.is_authenticated else None

        if 'user' in s_or_r:
            if s_or_r['user'].is_authenticated:
                return s_or_r['user']

        return None

    @classmethod
    def get_cookie(cls, s_or_r: ScopeOrRequest, name: str) -> Optional[str]:
        if isinstance(s_or_r, django.http.HttpRequest):
            return s_or_r.COOKIES.get(name)
        return s_or_r.get('cookies', {}).get(name)

    @classmethod
    def get_header(cls, s_or_r: ScopeOrRequest, name: str) -> str:
        if isinstance(s_or_r, django.http.HttpRequest):
            return s_or_r.headers.get(name, '')
        for (k, v) in s_or_r['headers']:
            if k.decode().lower() == name.lower():
                return v.decode()
        return ''

    @classmethod
    def is_from_another_page(cls, s_or_r: ScopeOrRequest) -> bool:
        # Every tunnel on settings.TUNNEL_DOMAIN is the same site to a browser, so a page in
        # one tunnel could send requests to another with that tunnel's cookie. Following a link
        # to a tunnel is still allowed.
        if isinstance(s_or_r, django.http.HttpRequest):
            return (
                s_or_r.headers.get('Sec-Fetch-Site') in ('same-site', 'cross-site') and not (
                    s_or_r.headers.get('Sec-Fetch-Mode') == 'navigate' and
                    s_or_r.method in ('GET', 'HEAD')
                )
            )
        origin = cls.get_header(s_or_r, 'origin')
        return bool(origin) and origin.split('://', 1)[-1].lower() != cls.get_host(s_or_r).lower()

    @classmethod
    def _tunnel_session_user(
        cls, s_or_r: ScopeOrRequest, tunnel: OctoPrintTunnel
    ) -> Optional[User]:
        value = cls.get_cookie(s_or_r, TUNNEL_SESSION_COOKIE_NAME)
        if not value or cls.is_from_another_page(s_or_r):
            return None
        try:
            data = signing.loads(value, salt=TUNNEL_SESSION_SALT, max_age=settings.SESSION_COOKIE_AGE)
        except signing.BadSignature:  # also raised when the cookie is too old
            return None

        user = tunnel.printer.user
        if (
            data.get('tunnel') == tunnel.id and
            data.get('user') == user.id and
            user.is_active and
            constant_time_compare(data.get('auth', ''), user.get_session_auth_hash())
        ):
            return user
        return None

    @classmethod
    def _validate_tunnel_session(
        cls, s_or_r: ScopeOrRequest, tunnel: OctoPrintTunnel
    ) -> OctoPrintTunnel:
        user = cls._get_user(s_or_r)
        if user is not None and user.is_authenticated:
            if tunnel.printer.user_id == user.id:
                return

            raise PermissionDenied

        if cls._tunnel_session_user(s_or_r, tunnel) is not None:
            return

        raise TunnelAuthenticationError('missing session', realm=None)

    @classmethod
    def _validate_tunnel_basic_auth(
        cls, s_or_r: ScopeOrRequest, tunnel: OctoPrintTunnel
    ) -> OctoPrintTunnel:
        auth_header = cls.get_authorization_header(s_or_r)

        realm = (
            f'tunnel {tunnel.subdomain_code}'
            if tunnel.subdomain_code else
            f'tunnel {tunnel.port}'
        )

        try:
            scheme, raw_token = auth_header.split()
        except ValueError:
            scheme, raw_token = None, None

        if scheme and scheme.lower() == 'basic':
            try:
                username, password = base64.b64decode(
                    raw_token).decode().split(':')
            except (binascii.Error, ValueError):
                raise TunnelAuthenticationError(
                    'invalid token', realm=realm)

            if (
                tunnel.basicauth_username == username and
                check_password(password, tunnel.basicauth_password)
            ):
                if isinstance(s_or_r, django.http.HttpRequest):
                    setattr(s_or_r, 'auth_header', auth_header)
                else:
                    s_or_r['auth_header'] = auth_header
                return

            raise TunnelAuthenticationError(
                'invalid credentials', realm=realm)

        raise TunnelAuthenticationError('missing credentials', realm=realm)

    @classmethod
    def get_octoprinttunnel(
        cls, s_or_r: ScopeOrRequest
    ) -> OctoPrintTunnel:
        subdomain_code = cls.get_subdomain_code(s_or_r)
        port = cls.get_port(s_or_r)
        LOGGER.debug(
            ('get_octoprinttunnel', port, subdomain_code)
        )

        if subdomain_code:
            qs_kwargs = {'subdomain_code':  subdomain_code}
        elif port:   # Port should be present when subdomain_code is missing
            qs_kwargs = {'port': port}
        else:
            raise TunnelAuthenticationError('invalid credentials', realm=None)

        qs = OctoPrintTunnel.objects.filter(
            **qs_kwargs
        ).select_related('printer', 'printer__user')

        # do we have a subdomain/port matching tunnel at all?
        tunnel = qs.first()
        if tunnel is None:
            raise TunnelAuthenticationError('invalid credentials', realm=None)

        if tunnel.basicauth_username:
            # An app's page opened from the tunnel's old address is signed in with a cookie;
            # see tunnelv2_views.redirect_page_to_tunnel_domain
            if cls._tunnel_session_user(s_or_r, tunnel) is None:
                cls._validate_tunnel_basic_auth(s_or_r, tunnel)
        else:
            cls._validate_tunnel_session(s_or_r, tunnel)
        return tunnel

    @classmethod
    def is_tunnel_request(cls, s_or_r: ScopeOrRequest) -> bool:
        if settings.OCTOPRINT_TUNNEL_PORT_RANGE:
            return cls.get_port(s_or_r) in settings.OCTOPRINT_TUNNEL_PORT_RANGE
        return cls.get_subdomain_code(s_or_r)
