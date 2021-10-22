from typing import Optional, Union

import base64
import binascii

# from asgiref.typing import HTTPScope
import django.http

from django.conf import settings
from django.db.models import Q

from app.models import User, Printer, PrinterTunnel

HTTPScope = dict
ScopeOrRequest = Union[HTTPScope, django.http.HttpRequest]


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
            import logging
            logging.error(s_or_r.headers)
            return s_or_r.headers.get('Authorization', '').strip()

        try:
            authorization = [
                hpair[1]
                for hpair in s_or_r['headers']
                if hpair[0] == b'authorization'
            ][0]
        except IndexError:
            return ''

        return authorization.decode()

    @classmethod
    def _get_user(cls, s_or_r: ScopeOrRequest) -> Optional[User]:
        if isinstance(s_or_r, django.http.HttpRequest):
            return s_or_r.user

        if 'user' in s_or_r and isinstance(s_or_r['user'], User):
            return s_or_r['user']

        return None

    @classmethod
    def get_printer(cls, s_or_r: ScopeOrRequest) -> Optional[Printer]:
        port = cls.get_port(s_or_r)
        subdomain_code = cls.get_subdomain_code(s_or_r)
        auth_header = cls.get_authorization_header(s_or_r)
        import logging

        qs = PrinterTunnel.objects.filter(
            Q(port=port) | Q(subdomain_code=subdomain_code),
        ).select_related('printer', 'printer__user')

        logging.error((port, subdomain_code, auth_header, qs))

        try:
            scheme, raw_token = auth_header.split()
        except ValueError:
            scheme, raw_token = None, None

        if scheme and scheme.lower() == 'basic':
            try:
                username, password = base64.b64decode(
                    raw_token).decode().split(':')
            except (binascii.Error, ValueError):
                return None  # FIXME raise http error?

            pt = qs.filter(
                basicauth_username=username,
                basicauth_password=password,
            ).first()
            return pt.printer if pt else None

        user = cls._get_user(s_or_r)
        if user is not None:
            if user.is_authenticated:
                pt = qs.filter(
                    printer__user_id=user.id,
                ).first()
                return pt.printer if pt else None

        return None

    @classmethod
    def is_tunnel_request(cls, s_or_r: ScopeOrRequest) -> bool:
        port = cls.get_port(s_or_r)
        return (
            cls.get_subdomain_code(s_or_r) or
            (
                port >= settings.OCTOPRINT_TUNNEL_PORT_RANGE[0] and
                port < settings.OCTOPRINT_TUNNEL_PORT_RANGE[1]
            )
        )
