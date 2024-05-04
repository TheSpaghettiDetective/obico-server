from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

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
    def is_unique_email(self, email):
        return not self.user_model.objects.filter(email=email, site=self.request.site).exists()

    def save_user(self, request, user, form, commit=True):
        user.site = get_current_site(request)
        user.username = f'{user.email}_{user.site.id}'
        return super().save_user(request, user, form, commit)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        email = sociallogin.account.extra_data.get('email', '').strip().lower()
        if not email:
            return

        # verify we have a verified email address
        # https://github.com/pennersr/django-allauth/issues/418
        # google provider might not have working sociallogin.email_addresses (buggy allauth version?)
        # so we are checking extra_data first
        email_verified: bool = sociallogin.account.extra_data.get('email_verified', False)
        if email_verified is not True:
            for _email in sociallogin.email_addresses:
                if _email.email.lower() == email and _email.verified:
                    email_verified = True
                    break

        if not email_verified:
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email_address = EmailAddress.objects.get(email__iexact=email)  # FIXME verified=True?
        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        user = email_address.user
        sociallogin.connect(request, user)
