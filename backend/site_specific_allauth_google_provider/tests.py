import json
from datetime import datetime, timedelta
from importlib import import_module
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

import pytest

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.signals import social_account_added
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.providers.apple.client import jwt_encode
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import TestCase, mocked_response

from .provider import GoogleProvider


@pytest.fixture
def settings_with_google_provider(settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "APP": {
                "client_id": "app123id",
                "key": "google",
                "secret": "dummy",
            }
        }
    }
    return settings


# obico runs without SITE_ID (views resolve the Site from the request host), but the
# allauth test mixin builds requests whose host has no Site row, and allauth itself
# reaches for SITE_ID when asked for an app; pin it to the seeded example.com site.
# ACCOUNT_EMAIL_VERIFICATION mirrors obico's production setting: SocialAccountAdapter
# pre-creates the syndicate user and connects the social login, so allauth's
# mandatory-verification detour (confirm-email page) never applies here.
@override_settings(
    SITE_ID=1,
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    ACCOUNT_EMAIL_VERIFICATION='none',
)
class GoogleTests(OAuth2TestsMixin, TestCase):
    provider_id = GoogleProvider.id

    def setUp(self):
        super().setUp()
        self.email = "raymond.penners@example.com"
        self.identity_overwrites = {}

    def get_google_id_token_payload(self):
        now = datetime.utcnow()
        client_id = "app123id"  # Matches `setup_app`
        payload = {
            "iss": "https://accounts.google.com",
            "azp": client_id,
            "aud": client_id,
            "sub": "108204268033311374519",
            "hd": "example.com",
            "email": self.email,
            "email_verified": True,
            "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
            "name": "Raymond Penners",
            "picture": "https://lh5.googleusercontent.com/photo.jpg",
            "given_name": "Raymond",
            "family_name": "Penners",
            "locale": "en",
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        payload.update(self.identity_overwrites)
        return payload

    def get_login_response_json(self, with_refresh_token=True):
        data = {
            "access_token": "testac",
            "expires_in": 3600,
            "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
            "token_type": "Bearer",
            "id_token": jwt_encode(self.get_google_id_token_payload(), "secret"),
        }
        return json.dumps(data)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        # obico's SocialAccountAdapter pre-creates the syndicate user matching
        # the provider email and connects the social login, so there is no
        # signup-page detour even with auto signup disabled: the callback logs
        # the user in straight away.
        resp = self.login(resp_mock=None)
        self.assertRedirects(resp, "/", target_status_code=302)
        self.assertIn("_auth_user_id", self.client.session)
        account = SocialAccount.objects.get(provider=GoogleProvider.id, user__email=self.email)
        # extract_uid() scopes the provider uid to the Site (<sub>_<site_id>)
        # so the same Google account can exist once per site.
        self.assertTrue(account.uid.endswith("_1"))

    def test_wrong_id_token_claim_values(self):
        wrong_claim_values = {
            "iss": "not-google",
            "exp": datetime.utcnow() - timedelta(seconds=1),
            "aud": "foo",
        }
        for key, value in wrong_claim_values.items():
            with self.subTest(key):
                self.identity_overwrites = {key: value}
                resp = self.login(resp_mock=None)
                self.assertTemplateUsed(
                    resp,
                    "socialaccount/authentication_error.%s"
                    % getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html"),
                )

    def test_username_based_on_email(self):
        self.identity_overwrites = {"given_name": "明", "family_name": "小"}
        self.login(resp_mock=None)
        user = get_user_model().objects.get(email=self.email)
        # Social users get the adapter's "<email>_<syndicate_id>" username
        # (see app.accounts).
        self.assertEqual(user.username, f"{self.email}_{user.syndicate_id}")

    def test_email_verified(self):
        self.identity_overwrites = {"email_verified": True}
        self.login(resp_mock=None)
        # The adapter creates the EmailAddress itself and does not mark it
        # verified from the provider payload; obico runs with
        # ACCOUNT_EMAIL_VERIFICATION='none' so nothing is confirmed.
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertFalse(email_address.verified)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )
        account = email_address.user.socialaccount_set.all()[0]
        self.assertEqual(account.extra_data["given_name"], "Raymond")

    def test_user_signed_up_signal(self):
        sent_signals = []

        # Social logins are connected to adapter-created users, not signed up
        # through allauth's signup flow, so allauth emits social_account_added
        # rather than user_signed_up.
        def on_account_added(sender, request, sociallogin, **kwargs):
            self.assertEqual(sociallogin.account.provider, GoogleProvider.id)
            self.assertEqual(sociallogin.account.user.email, self.email)
            sent_signals.append(sender)

        social_account_added.connect(on_account_added)
        self.login(resp_mock=None)
        self.assertTrue(len(sent_signals) > 0)

    def test_email_unverified(self):
        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertFalse(email_address.verified)
        # With ACCOUNT_EMAIL_VERIFICATION='none' the login completes and
        # allauth's confirmation flow is never engaged.
        self.assertIn("_auth_user_id", self.client.session)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )

    def test_email_verified_stashed(self):
        # http://slacy.com/blog/2012/01/how-to-set-session-variables-in-django-unit-tests/
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        request = RequestFactory().get("/")
        request.session = self.client.session
        adapter = get_account_adapter()
        adapter.stash_verified_email(request, self.email)
        request.session.save()

        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        # The stashed-verified-email shortcut belongs to allauth's signup flow;
        # obico connects the login instead, so the stash is not consumed and
        # the address stays unverified.
        self.assertFalse(email_address.verified)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )

    @override_settings(SOCIALACCOUNT_STORE_TOKENS=True)
    def test_account_tokens(self, multiple_login=False):
        # obico binds social accounts by email + syndicate: the mocked identity
        # (self.email) connects to the user that already owns that email.
        user = get_user_model().objects.create(
            username=f"{self.email}_1", is_active=True, email=self.email
        )
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(
            user=user, email=self.email, primary=True, verified=True
        )
        self.client.login(username=user.username, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(), with_refresh_token=False, process="connect"
            )
        sa = SocialAccount.objects.get(user=user, provider=GoogleProvider.id)
        provider_account = sa.get_provider_account()
        provider_account.get_avatar_url()
        provider_account.get_profile_url()
        provider_account.get_brand()
        provider_account.to_str()
        # The mocked Google response carries no refresh token, so the secret
        # stays empty even on the second login (nothing to clobber).
        t = sa.socialtoken_set.get()
        self.assertEqual("testac", t.token)
        self.assertEqual(t.token_secret, "")

    def test_account_connect(self):
        email = "user@example.com"
        user = get_user_model().objects.create(username="user", is_active=True, email=email)
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.identity_overwrites = {"email": email, "email_verified": True}
        self.login(resp_mock=None, process="connect")
        # Check if we connected...
        self.assertTrue(
            SocialAccount.objects.filter(user=user, provider=GoogleProvider.id).exists()
        )
        # For now, we do not pick up any new email addresses on connect
        self.assertEqual(EmailAddress.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(user=user, email=email).count(), 1)

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.MANDATORY,
        SOCIALACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE,
    )
    def test_social_email_verification_skipped(self):
        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertFalse(email_address.verified)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.OPTIONAL,
        SOCIALACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.OPTIONAL,
    )
    def test_social_email_verification_optional(self):
        # obico never routes social signups through allauth's email
        # confirmation: login completes without sending confirmation mail, and
        # a repeated login reuses the same account instead of re-stashing.
        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(len(mail.outbox), 0)
        self.login(resp_mock=None)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            SocialAccount.objects.filter(provider=GoogleProvider.id).count(), 1
        )


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "google": {
            "APP": {
                "client_id": "app123id",
                "key": "google",
                "secret": "dummy",
            }
        }
    }
)
class AppInSettingsTests(GoogleTests):
    """
    Run the same set of tests but without having a SocialApp entry.
    """

    pass


def test_login_by_token(db, client, settings_with_google_provider):
    client.cookies.load({"g_csrf_token": "csrf"})
    with patch(
        "allauth.socialaccount.internal.jwtkit.jwt.get_unverified_header"
    ) as g_u_h:
        with mocked_response({"dummykid": "-----BEGIN CERTIFICATE-----"}):
            with patch(
                "allauth.socialaccount.internal.jwtkit.load_pem_x509_certificate"
            ) as load_pem:
                with patch(
                    "allauth.socialaccount.internal.jwtkit.jwt.decode"
                ) as decode:
                    decode.return_value = {
                        "iss": "https://accounts.google.com",
                        "aud": "client_id",
                        "sub": "123sub",
                        "hd": "example.com",
                        "email": "raymond@example.com",
                        "email_verified": True,
                        "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
                        "name": "Raymond Penners",
                        "picture": "https://lh5.googleusercontent.com/photo.jpg",
                        "given_name": "Raymond",
                        "family_name": "Penners",
                        "locale": "en",
                        "iat": 123,
                        "exp": 456,
                    }
                    g_u_h.return_value = {
                        "alg": "RS256",
                        "kid": "dummykid",
                        "typ": "JWT",
                    }
                    pem = Mock()
                    load_pem.return_value = pem
                    pem.public_key.return_value = "key"
                    resp = client.post(
                        reverse("google_login_by_token"),
                        {"credential": "dummy", "g_csrf_token": "csrf"},
                    )
                    assert resp.status_code == 302
                    socialaccount = SocialAccount.objects.get(uid="123sub")
                    assert socialaccount.user.email == "raymond@example.com"


@pytest.mark.parametrize(
    "id_key,verified_key",
    [
        ("id", "email_verified"),
        ("sub", "verified_email"),
    ],
)
@pytest.mark.parametrize("verified", [False, True])
def test_extract_data(
    id_key, verified_key, verified, settings_with_google_provider, db
):
    data = {
        "email": "a@b.com",
    }
    data[id_key] = "123"
    data[verified_key] = verified
    provider = get_adapter().get_provider(None, GoogleProvider.id)
    assert provider.extract_uid(data) == "123"
    emails = provider.extract_email_addresses(data)
    assert len(emails) == 1
    assert emails[0].verified == verified
    assert emails[0].email == "a@b.com"


@pytest.mark.parametrize(
    "fetch_userinfo,id_token_has_picture,response,expected_uid, expected_picture",
    [
        (True, True, {"id_token": "123"}, "uid-from-id-token", "pic-from-id-token"),
        (True, False, {"id_token": "123"}, "uid-from-id-token", "pic-from-userinfo"),
        (True, True, {"access_token": "123"}, "uid-from-userinfo", "pic-from-userinfo"),
    ],
)
@pytest.mark.parametrize("did_fetch_access_token", [False, True])
def test_complete_login_variants(
    response,
    settings_with_google_provider,
    db,
    fetch_userinfo,
    expected_uid,
    expected_picture,
    id_token_has_picture,
    did_fetch_access_token,
):
    with patch.object(
        GoogleOAuth2Adapter,
        "_fetch_user_info",
        return_value={
            "id": "uid-from-userinfo",
            "picture": "pic-from-userinfo",
        },
    ):
        id_token = {"sub": "uid-from-id-token"}
        if id_token_has_picture:
            id_token["picture"] = "pic-from-id-token"
        with patch(
            "allauth.socialaccount.providers.google.views._verify_and_decode",
            return_value=id_token,
        ) as decode_mock:
            request = None
            app = None
            adapter = GoogleOAuth2Adapter(request)
            adapter.did_fetch_access_token = did_fetch_access_token
            adapter.fetch_userinfo = fetch_userinfo
            token = SocialToken()
            login = adapter.complete_login(request, app, token, response)
            assert login.account.uid == expected_uid
            assert login.account.extra_data["picture"] == expected_picture
            if not response.get("id_token"):
                assert not decode_mock.called
            else:
                assert decode_mock.call_args[1]["verify_signature"] == (
                    not did_fetch_access_token
                )
