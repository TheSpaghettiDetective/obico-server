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
            site = get_current_site(request)
            try:
                user = UserModel.objects.get(email=username, site=site)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None


class SiteSpecificAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user.site = get_current_site(request)
        user.username = f'{user.email}_{user.site.id}'
        return super().save_user(request, user, form, commit)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        import pdb; pdb.set_trace()
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        site_id = get_current_site(request).id
        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        email = sociallogin.account.extra_data.get('email', '').strip().lower()
        if not email:
            raise PermissionDenied('Email not exist in social login data.')

        user = User.objects.filter(emailaddress__email__iexact=email, site_id=site_id).first()
        if not user:
            user = User.objects.get_or_create(
                email=email,
                site_id=site_id,
                defaults={
                    'password': make_password(secrets.token_hex(16)),
                    'username': f'{email}_{site_id}',
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
