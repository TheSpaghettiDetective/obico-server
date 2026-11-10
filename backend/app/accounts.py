from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from ipware import get_client_ip as ipware_client_ip
from app.models import User
from django.contrib.auth.hashers import make_password
import secrets

from lib.syndicate import syndicate_from_request, brand_from_request, brand_settings

from django.utils.encoding import force_str
from django.conf import settings


def users_by_email(email, syndicate, is_active=None):
    """The accounts in one syndicate that an address belongs to, by their
    EmailAddress rows or their own email. allauth's own lookup
    (filter_users_by_email) looks across every syndicate, so none of our paths
    calls it."""
    users = User.objects.filter(Q(emailaddress__email__iexact=email) | Q(email__iexact=email), syndicate=syndicate)
    if is_active is not None:
        users = users.filter(is_active=is_active)
    return list(users.distinct())


class SyndicateSpecificBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if request is None or username is None:
            return None
        users = users_by_email(username, syndicate_from_request(request))
        if len(users) > 1:
            raise User.MultipleObjectsReturned(f'{len(users)} accounts in one syndicate share an address')
        if users and users[0].check_password(password):
            return users[0]
        return None


class SyndicateSpecificAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user.syndicate = syndicate_from_request(request)
        return super().save_user(request, user, form, commit)

    def populate_username(self, request, user):
        user.username = f'{user.email}_{user.syndicate.id}'

    def pre_login(self, request, user, **kwargs):
        # Every lookup that finds the account keeps to the request's syndicate.
        syndicate = syndicate_from_request(request)
        if user.syndicate_id != syndicate.id:
            raise AssertionError(f'Signing in to a {user.syndicate.name} account on a {syndicate.name} request')
        return super().pre_login(request, user, **kwargs)

    def get_from_email(self):
        return brand_settings(brand_from_request(self.request)).get('from_email', settings.DEFAULT_FROM_EMAIL)

    def format_email_subject(self, subject):
        return force_str(subject)

    def get_client_ip(self, request):
        # allauth's rate limits count per client IP. Behind a proxy, allauth
        # itself now uses the proxy's address unless told how many proxies to
        # trust, so every user would share one limit. Read the IP the way the
        # rest of the server does (app/middleware.py), from X-Forwarded-For.
        client_ip, _ = ipware_client_ip(request)
        if not client_ip:
            raise PermissionDenied('Unable to determine client IP address')
        return client_ip

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        syndicate_name = brand_settings(brand_from_request(request)).get('display_name', "Obico")

        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "key": emailconfirmation.key,
            "syndicate_name": syndicate_name,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        syndicate = syndicate_from_request(request)
        syndicate_id = syndicate.id
        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        email = sociallogin.account.extra_data.get('email', '').strip().lower()
        if not email:
            raise PermissionDenied('Email not exist in social login data.')

        users = users_by_email(email, syndicate)
        user = users[0] if users else None
        if not user:
            user = User.objects.get_or_create(
                email=email,
                syndicate_id=syndicate_id,
                defaults={
                    'password': make_password(secrets.token_hex(16)),
                    'username': f'{email}_{syndicate_id}',
                    'is_active': True,
                })[0]
            EmailAddress.objects.get_or_create(
                user=user,
                email=email,
                defaults={
                    'primary': True,
                }
            )

        sociallogin.connect(request, user)
