from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from app.models import User
from django.contrib.auth.hashers import make_password
import secrets

from lib.syndicate import syndicate_from_request, settings_for_syndicate

from django.utils.encoding import force_str
from django.conf import settings


class SyndicateSpecificBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        UserModel = get_user_model()
        if request is not None:
            syndicate = syndicate_from_request(request)
            try:
                user = UserModel.objects.get(email__iexact=username, syndicate=syndicate)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None


class SyndicateSpecificAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user.syndicate = syndicate_from_request(request)
        return super().save_user(request, user, form, commit)

    def populate_username(self, request, user):
        user.username = f'{user.email}_{user.syndicate.id}'

    def get_from_email(self):
        syndicate = syndicate_from_request(self.request)
        from_email = settings_for_syndicate(syndicate.name).get('from_email', settings.DEFAULT_FROM_EMAIL)
        return from_email

    def format_email_subject(self, subject):
        return force_str(subject)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        syndicate = syndicate_from_request(request)
        syndicate_name = settings_for_syndicate(syndicate.name).get('display_name', "Obico")

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

        syndicate_id = syndicate_from_request(request).id
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
