"""Test helpers for the provider's tests, copied from django-allauth 65.21.1.

allauth 0.63 shipped these inside the installed package
(allauth.socialaccount.tests.OAuth2TestsMixin, allauth.tests.mocked_response).
Later releases keep them in the repository's tests/ directory, which is not
installed, so the parts tests.py uses are copied here unchanged from
tests/mocking.py and tests/apps/socialaccount/base.py.

django-allauth is MIT licensed: Copyright (c) 2010-2026 Raymond Penners and
contributors.
"""
import base64
import hashlib
import json
import requests
import uuid
import warnings
from http import HTTPStatus
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

import allauth.app_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount, SocialApp


class MockedResponse:
    def __init__(self, status_code, content, headers=None):
        if headers is None:
            headers = {}

        self.status_code = status_code
        if isinstance(content, dict):
            content = json.dumps(content)
            headers["content-type"] = "application/json"
        self.content = content.encode("utf8")
        self.headers = headers

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        pass

    @property
    def ok(self):
        return self.status_code // 100 == 2

    @property
    def text(self):
        return self.content.decode("utf8")


class mocked_response:
    def __init__(self, *responses, callback=None):
        self.callback = callback
        self.responses = list(responses)

    def __enter__(self):
        self.orig_get = requests.Session.get
        self.orig_post = requests.Session.post
        self.orig_request = requests.Session.request

        def mockable_request(f):
            def new_f(*args, **kwargs):
                if self.callback:
                    response = self.callback(*args, **kwargs)
                    if response is not None:
                        return response
                if self.responses:
                    resp = self.responses.pop(0)
                    if isinstance(resp, dict):
                        resp = MockedResponse(HTTPStatus.OK, resp)
                    return resp
                return f(*args, **kwargs)

            return Mock(side_effect=new_f)

        requests.Session.get = mockable_request(requests.Session.get)
        requests.Session.post = mockable_request(requests.Session.post)
        requests.Session.request = mockable_request(requests.Session.request)

    def __exit__(self, type, value, traceback):
        requests.Session.get = self.orig_get
        requests.Session.post = self.orig_post
        requests.Session.request = self.orig_request


def setup_app(provider_id):
    request = RequestFactory().get("/")
    apps = get_adapter().list_apps(request, provider_id)
    if apps:
        return apps[0]

    app = SocialApp.objects.create(
        provider=provider_id,
        name=provider_id,
        client_id="app123id",
        key=provider_id,
        secret="dummy",
    )
    if allauth.app_settings.SITES_ENABLED:
        from django.contrib.sites.models import Site

        app.sites.add(Site.objects.get_current())
    return app


class OAuth2TestsMixin:
    provider_id: str

    def get_mocked_response(self):
        pass

    def get_expected_to_str(self):
        raise NotImplementedError

    def get_access_token(self) -> str:
        return "testac"

    def get_refresh_token(self) -> str:
        return "testrf"

    def get_login_response_json(self, with_refresh_token=True):
        response = {
            "uid": uuid.uuid4().hex,
            "access_token": self.get_access_token(),
        }
        if with_refresh_token:
            response["refresh_token"] = self.get_refresh_token()
        return json.dumps(response)

    def mocked_response(self, *responses):
        return mocked_response(*responses)

    def setUp(self):
        super().setUp()
        self.setup_provider()

    def setup_provider(self):
        self.app = setup_app(self.provider_id)
        self.request = RequestFactory().get("/")
        self.provider = self.app.get_provider(self.request)

    def test_provider_has_no_pkce_params(self):
        provider_settings = app_settings.PROVIDERS.get(self.app.provider, {})
        provider_settings_with_pkce_set = provider_settings.copy()
        provider_settings_with_pkce_set["OAUTH_PKCE_ENABLED"] = False

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={self.app.provider: provider_settings_with_pkce_set}
        ):
            self.assertEqual(self.provider.get_pkce_params(), {})

    def test_provider_has_pkce_params(self):
        provider_settings = app_settings.PROVIDERS.get(self.app.provider, {})
        provider_settings_with_pkce_set = provider_settings.copy()
        provider_settings_with_pkce_set["OAUTH_PKCE_ENABLED"] = True

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={self.app.provider: provider_settings_with_pkce_set}
        ):
            pkce_params = self.provider.get_pkce_params()
            self.assertEqual(
                set(pkce_params.keys()),
                {"code_challenge", "code_challenge_method", "code_verifier"},
            )
            hashed_verifier = hashlib.sha256(
                pkce_params["code_verifier"].encode("ascii")
            )
            code_challenge = base64.urlsafe_b64encode(hashed_verifier.digest())
            code_challenge_without_padding = code_challenge.rstrip(b"=")
            assert pkce_params["code_challenge"] == code_challenge_without_padding

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp_mock = self.get_mocked_response()
        if not resp_mock:
            warnings.warn(f"Cannot test provider {self.provider.id}, no oauth mock")
            return
        resp = self.login(
            resp_mock,
        )
        self.assertRedirects(resp, reverse("socialaccount_signup"))

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login_with_pkce_disabled(self):
        provider_settings = app_settings.PROVIDERS.get(self.app.provider, {})
        provider_settings_with_pkce_disabled = provider_settings.copy()
        provider_settings_with_pkce_disabled["OAUTH_PKCE_ENABLED"] = False

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={
                self.app.provider: provider_settings_with_pkce_disabled
            }
        ):
            resp_mock = self.get_mocked_response()
            if not resp_mock:
                warnings.warn(f"Cannot test provider {self.provider.id}, no oauth mock")
                return
            resp = self.login(
                resp_mock,
            )
            self.assertRedirects(resp, reverse("socialaccount_signup"))

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login_with_pkce_enabled(self):
        provider_settings = app_settings.PROVIDERS.get(self.app.provider, {})
        provider_settings_with_pkce_enabled = provider_settings.copy()
        provider_settings_with_pkce_enabled["OAUTH_PKCE_ENABLED"] = True
        with self.settings(
            SOCIALACCOUNT_PROVIDERS={
                self.app.provider: provider_settings_with_pkce_enabled
            }
        ):
            resp_mock = self.get_mocked_response()
            if not resp_mock:
                warnings.warn(f"Cannot test provider {self.provider.id}, no oauth mock")
                return

            resp = self.login(
                resp_mock,
            )
            self.assertRedirects(resp, reverse("socialaccount_signup"))

    @override_settings(SOCIALACCOUNT_STORE_TOKENS=True)
    def test_account_tokens(self, multiple_login=False):
        email = "user@example.com"
        user = get_user_model()(is_active=True)
        user_email(user, email)
        user_username(user, "user")
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(),
                with_refresh_token=False,
                process="connect",
            )
        # get account
        sa = SocialAccount.objects.filter(
            user=user, provider=self.provider.app.provider_id or self.provider.id
        ).get()
        provider_account = sa.get_provider_account()
        self.assertEqual(provider_account.to_str(), self.get_expected_to_str())
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account.get_avatar_url()
        provider_account.get_profile_url()
        provider_account.get_brand()
        # get token
        if self.app:
            t = sa.socialtoken_set.get()
            # verify access_token and refresh_token
            self.assertEqual(self.get_access_token(), t.token)
            resp = json.loads(self.get_login_response_json(with_refresh_token=True))
            if "refresh_token" in resp:
                refresh_token = resp.get("refresh_token")
            elif "refreshToken" in resp:
                refresh_token = resp.get("refreshToken")
            else:
                refresh_token = ""
            self.assertEqual(t.token_secret, refresh_token)

    @override_settings(SOCIALACCOUNT_STORE_TOKENS=True)
    def test_account_refresh_token_saved_next_login(self):
        """
        fails if a login missing a refresh token, deletes the previously
        saved refresh token. Systems such as google's oauth only send
        a refresh token on first login.
        """
        self.test_account_tokens(multiple_login=True)

    def login(self, resp_mock=None, process="login", with_refresh_token=True):
        with self.mocked_response():
            resp = self.client.post(
                self.provider.get_login_url(self.request, process=process)
            )
        p = urlparse(resp["location"])
        q = parse_qs(p.query)

        pkce_enabled = app_settings.PROVIDERS.get(self.app.provider, {}).get(
            "OAUTH_PKCE_ENABLED", self.provider.pkce_enabled_default
        )

        self.assertEqual("code_challenge" in q, pkce_enabled)
        self.assertEqual("code_challenge_method" in q, pkce_enabled)
        if pkce_enabled:
            code_challenge = q["code_challenge"][0]
            self.assertEqual(q["code_challenge_method"][0], "S256")

        complete_url = self.provider.get_callback_url()
        self.assertGreater(q["redirect_uri"][0].find(complete_url), 0)
        response_json = self.get_login_response_json(
            with_refresh_token=with_refresh_token
        )

        if isinstance(resp_mock, list):
            resp_mocks = resp_mock
        elif resp_mock is None:
            resp_mocks = []
        else:
            resp_mocks = [resp_mock]

        with self.mocked_response(
            MockedResponse(
                HTTPStatus.OK, response_json, {"content-type": "application/json"}
            ),
            *resp_mocks,
        ):
            resp = self.client.get(complete_url, self.get_complete_parameters(q))

            # Find the access token POST request, and assert that it contains
            # the correct code_verifier if and only if PKCE is enabled
            request_calls = requests.Session.request.call_args_list
            for args, kwargs in request_calls:
                data = kwargs.get("data", {})
                if (
                    args[0] == "POST"
                    and isinstance(data, dict)
                    and data.get("redirect_uri", "").endswith(complete_url)
                ):
                    self.assertEqual("code_verifier" in data, pkce_enabled)

                    if pkce_enabled:
                        hashed_code_verifier = hashlib.sha256(
                            data["code_verifier"].encode("ascii")
                        )
                        expected_code_challenge = (
                            base64.urlsafe_b64encode(hashed_code_verifier.digest())
                            .rstrip(b"=")
                            .decode()
                        )
                        self.assertEqual(code_challenge, expected_code_challenge)

        return resp

    def get_complete_parameters(self, q):
        return {"code": "test", "state": q["state"][0]}

    def test_authentication_error(self):
        resp = self.client.get(self.provider.get_callback_url())
        template_ext = getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html")
        self.assertTemplateUsed(
            resp, f"socialaccount/authentication_error.{template_ext}"
        )
