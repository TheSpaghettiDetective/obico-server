from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from channels.auth import AuthMiddlewareStack

from app.models import Printer


class PrinterAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key, request=None):
        try:
            printer = Printer.objects.select_related('user').get(auth_token=key)
        except ObjectDoesNotExist:
            raise AuthenticationFailed({'error': 'Invalid or Inactive Token', 'is_authenticated': False})

        return printer.user, printer


def TokenAuthMiddlewareStack(inner): return AuthMiddlewareStack(inner)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
