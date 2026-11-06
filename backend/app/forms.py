from django.conf import settings
import logging
import requests
from django.db import models
from django import forms
from django.forms import ModelForm, Form, CharField, ChoiceField, Textarea, HiddenInput, BooleanField, ValidationError
from allauth.account.forms import SignupForm, LoginForm, AddEmailForm
import allauth.account.views
import phonenumbers
from pushbullet import Pushbullet, PushbulletError

from .widgets import CustomRadioSelectWidget
from .models import *
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import ResetPasswordForm
from allauth.account.adapter import get_adapter
from app.accounts import filter_users_by_email_and_syndicate
from lib.syndicate import syndicate_from_request


LOGGER = logging.getLogger(__name__)


class SocialAccountAwareLoginForm(LoginForm):
    no_password_yet: bool = False

    def clean(self):
        try:
            return super(SocialAccountAwareLoginForm, self).clean()
        except forms.ValidationError as err:
            if err.message == self.error_messages['email_password_mismatch']:
                email = self.user_credentials().get('email', None)
                if email is not None:
                    users = filter_users_by_email_and_syndicate(email, syndicate_from_request(self.request))
                    if any(not user.has_usable_password() and user.socialaccount_set.exists() for user in users):
                        self.no_password_yet = True
            raise err
    error_messages = {
        'email_password_mismatch': _("Invalid email or password."),
    }


class RecaptchaSignupForm(SignupForm):
    recaptcha_token = CharField(required=True)

    def clean(self):
        super().clean()

        # captcha verification
        recaptcha_token = self.cleaned_data.get('recaptcha_token')
        if not recaptcha_token:
            raise ValidationError('ReCAPTCHA is invalid.')

        data = {
            'response': recaptcha_token,
            'secret': settings.RECAPTCHA_SECRET_KEY
        }
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)

        if response.status_code == requests.codes.ok:
            if response.json()['success'] and response.json()['action'] == 'signup_form':
                LOGGER.debug('Captcha valid for user={}'.format(self.cleaned_data.get('email')))
            else:
                LOGGER.warn('Captcha invalid for user={}'.format(self.cleaned_data.get('email')))
                raise ValidationError('ReCAPTCHA is invalid.')
        else:
            LOGGER.error('Cannot validate reCAPTCHA for user={}'.format(self.cleaned_data.get('email')))

        return self.cleaned_data

class SyndicateSpecificResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        syndicate = syndicate_from_request(self.request)
        self.users = filter_users_by_email_and_syndicate(email, syndicate, is_active=True, prefer_verified=True)
        if not self.users:
            raise get_adapter().validation_error("unknown_email")
        return self.cleaned_data["email"]

class SyndicateSpecificAddEmailForm(AddEmailForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        syndicate = self.user.syndicate  # Assuming the user has a syndicate attribute

        # Check if a user with this email already exists in the same syndicate
        if filter_users_by_email_and_syndicate(email, syndicate):
            raise forms.ValidationError(_("A user is already registered with this email address."))

        return email
