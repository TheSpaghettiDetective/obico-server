from django.contrib.auth.decorators import login_required
from allauth.account.views import LoginView

from allauth.exceptions import ImmediateHttpResponse
from django.core.exceptions import PermissionDenied
from requests import RequestException
from allauth.socialaccount.providers.base import ProviderException

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
)
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)

from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)

class MobileLoginView(LoginView):

    def get_success_url(self):
        return '/mobile/fetch/'

@login_required
def fetch_session(request):
    return HttpResponse(f'<div id="view">{request.session.session_key}</div>')


def oauth_callback(request, *args, **kwargs):
    try:
        adapter = GoogleOAuth2Adapter(request)

        if 'error' in request.GET or 'code' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                adapter.provider_id,
                error=error)
        app = adapter.get_provider().get_app(request)

        callback_url = adapter.get_callback_url(request, app)
        provider = adapter.get_provider()
        scope = provider.get_scope(request)
        client = OAuth2Client(request, app.client_id, app.secret,
                                adapter.access_token_method,
                                adapter.access_token_url,
                                callback_url,
                                scope,
                                scope_delimiter=adapter.scope_delimiter,
                                headers=adapter.headers,
                                basic_auth=adapter.basic_auth)

        try:
            access_token = client.get_access_token(request.GET['code'])
            token = adapter.parse_token(access_token)
            token.app = app
            login = adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            return complete_social_login(request, login)
        except (PermissionDenied,
                OAuth2Error,
                RequestException,
                ProviderException) as e:
            return render_authentication_error(
                request,
                adapter.provider_id,
                exception=e)

    except ImmediateHttpResponse as e:
        return e.response
