from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from allauth.account.views import SignupView
from allauth.account.forms import SignupForm

from allauth.core.exceptions import ImmediateHttpResponse
from django.core.exceptions import PermissionDenied
from requests import RequestException
from allauth.socialaccount.providers.base import ProviderException

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
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

from .web_views import SocialAccountAwareLoginView

class MobileLoginView(SocialAccountAwareLoginView):
    template_name = 'mobile/account/login.html'

    def get_success_url(self):
        return '/mobile/auth/fetch/'

class MobileSignupView(SignupView):
    template_name = 'mobile/account/signup.html'

    def get_form_class(self):
        return SignupForm

    def get_success_url(self):
        return '/mobile/auth/fetch/'


@login_required
def fetch_session(request):
    return render(request, 'mobile/mobile_session_fetch.html', {'session_key': request.session.session_key})


def oauth_callback(request, *args, **kwargs):
    try:
        is_google = request.GET['provider'] == 'google'
        is_facebook = request.GET['provider'] == 'facebook'
        is_apple = request.GET['provider'] == 'apple'

        if is_google:
            adapter = GoogleOAuth2Adapter(request)
        elif is_facebook:
            adapter = FacebookOAuth2Adapter(request)
        elif is_apple:
            adapter = AppleOAuth2Adapter(request)
        else:
            raise Exception("Unsupported provider")

        provider = adapter.get_provider()
        app = provider.app

        try:
            if is_google:
                callback_url = adapter.get_callback_url(request, app)
                scope = provider.get_scope(request)
                client = OAuth2Client(
                    request,
                    app.client_id,
                    app.secret,
                    adapter.access_token_method,
                    adapter.access_token_url,
                    callback_url,
                    scope,
                    scope_delimiter=adapter.scope_delimiter,
                    headers=adapter.headers,
                    basic_auth=adapter.basic_auth)
                access_token = client.get_access_token(request.GET['code'])
                token = adapter.parse_token(access_token)
            elif is_facebook:
                access_token = request.GET['code']
                token = adapter.parse_token({'access_token': access_token, 'token_type': 'bearer', 'expires_in': 5179237})      # hard-coded properties to make allauth happy
            elif is_apple:
                access_token = request.GET['code']
                id_token = request.GET['id_token']
                refresh_token = request.GET.get('refresh_token', '')
                token = adapter.parse_token({
                    'access_token': access_token, 'id_token': id_token, 'refresh_token': refresh_token})

            token.app = app
            login = adapter.complete_login(
                request,
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

def apple_login(request):
    return render(request, 'mobile/account/apple_login.html')
