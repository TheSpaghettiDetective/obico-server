from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from channels.auth import AuthMiddlewareStack

from django.db import close_old_connections

from app.models import Printer, SharedResource


class PrinterAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key, request=None):
        try:
            printer = Printer.objects.select_related('user').get(auth_token=key)
        except ObjectDoesNotExist:
            raise AuthenticationFailed({'error': 'Invalid or Inactive Token', 'is_authenticated': False})

        return printer.user, printer


class PrinterWSAuthMiddleWare:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        close_old_connections()

        headers = dict(scope['headers'])
        try:
            if b'authorization' in headers:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'bearer':
                    printer = Printer.objects.select_related('user').get(auth_token=token_key)
                    printer.is_authenticated = True   # To make Printer duck-quack as authenticated User in Django Channels
                    scope['user'] = printer
            elif scope['path'].startswith('/ws/shared/'):
                printer = SharedResource.objects.select_related('printer').get(share_token=scope['path'].split(
                    '/')[-2]).printer  # scope['path'].split('/')[-2] is the share_token in uri
                printer.is_authenticated = True   # To make Printer duck-quack as authenticated User in Django Channels
                scope['user'] = printer
        except ObjectDoesNotExist:
            pass
        return self.inner(scope)


class PrinterServiceTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key, request=None):
        try:
            printer = Printer.objects.select_related('user').get(service_token=key)
        except ObjectDoesNotExist:
            raise AuthenticationFailed({'error': 'Invalid or Inactive Token', 'is_authenticated': False})

        return printer.user, printer


def TokenAuthMiddlewareStack(inner): return PrinterWSAuthMiddleWare(AuthMiddlewareStack(inner))


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
