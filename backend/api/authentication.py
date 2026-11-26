from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from channels.auth import AuthMiddlewareStack
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import TokenHasReadWriteScope

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


class ScopedOAuth2Authentication(OAuth2Authentication):
    """OAuth tokens, denied by default.

    A token signs a request in only on a view that declares `required_scopes`,
    which is what puts the view in the API for apps (website/docs/api/), and
    only when the token holds those scopes and also `read` to read or `write`
    to change anything. A view that also names `oauth_client_ids` takes only
    tokens issued to those apps. Everywhere else the token is ignored and the
    request counts as signed out; a browser session is not affected. A new view
    is therefore closed to apps until it declares its scopes."""

    def authenticate(self, request):
        view = (request.parser_context or {}).get('view')
        if not hasattr(view, 'required_scopes'):
            return None
        signed_in = super().authenticate(request)
        if signed_in is None:
            return None
        user, token = signed_in
        if user is None or not user.is_active:
            return None
        if not token.is_valid(TokenHasReadWriteScope().get_scopes(request, view)):
            return None
        client_ids = getattr(view, 'oauth_client_ids', None)
        if client_ids is not None and token.application.client_id not in client_ids:
            return None
        return signed_in
