from django.conf import settings
import logging
import requests
from django.db import models
from django import forms
from django.forms import ModelForm, Form, CharField, ChoiceField, Textarea, HiddenInput, BooleanField, ValidationError
from allauth.account.forms import SignupForm, LoginForm
import allauth.account.views
import phonenumbers
from pushbullet import Pushbullet, PushbulletError

from .widgets import CustomRadioSelectWidget
from .models import *
from django.utils.translation import gettext_lazy as _


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
                    user = User.objects.filter(email__iexact=email).first()
                    if user is not None and not user.has_usable_password():
                        has_social_accounts = user.socialaccount_set.exists()
                        if has_social_accounts:
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
