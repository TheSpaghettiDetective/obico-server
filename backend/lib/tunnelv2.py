from typing import Optional, Union

import logging
import base64
import binascii

# from asgiref.typing import HTTPScope
import django.http
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.exceptions import PermissionDenied
from app.models import User, OctoPrintTunnel

HTTPScope = dict
ScopeOrRequest = Union[HTTPScope, django.http.HttpRequest]

LOGGER = logging.getLogger(__name__)


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
    def get_subdomain_code(cls, s_or_r: ScopeOrRequest) -> str:
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
            if s_or_r.user.is_authenticated:
                return s_or_r.user

        if 'user' in s_or_r:
            if s_or_r['user'].is_authenticated:
                return s_or_r['user']

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
            cls._validate_tunnel_basic_auth(s_or_r, tunnel)
        else:
            cls._validate_tunnel_session(s_or_r, tunnel)
        return tunnel

    @classmethod
    def is_tunnel_request(cls, s_or_r: ScopeOrRequest) -> bool:
        if settings.OCTOPRINT_TUNNEL_PORT_RANGE:
            return cls.get_port(s_or_r) in settings.OCTOPRINT_TUNNEL_PORT_RANGE
        return cls.get_subdomain_code(s_or_r)
