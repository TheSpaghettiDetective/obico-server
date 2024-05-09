from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from app.models import User
from django.contrib.auth.hashers import make_password
import secrets


class SiteSpecificBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        UserModel = get_user_model()
        if request is not None:
            syndicate = get_current_site(request).syndicates.first()
            try:
                user = UserModel.objects.get(email=username.lower(), syndicate=syndicate)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None


class SiteSpecificAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user.syndicate = get_current_site(request).syndicates.first()
        return super().save_user(request, user, form, commit)

    def populate_username(self, request, user):
        user.username = f'{user.email}_{user.syndicate.id}'


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        syndicate_id = get_current_site(request).syndicates.first().id
        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        email = sociallogin.account.extra_data.get('email', '').strip().lower()
        if not email:
            raise PermissionDenied('Email not exist in social login data.')

        user = User.objects.filter(emailaddress__email__iexact=email, syndicate_id=syndicate_id).first()
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
