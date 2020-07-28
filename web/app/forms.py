from django.conf import settings
from django.db import models
from django.forms import ModelForm, Form, CharField, ChoiceField, Textarea, HiddenInput, BooleanField
import phonenumbers
from pushbullet import Pushbullet, PushbulletError

from .widgets import CustomRadioSelectWidget, PhoneCountryCodeWidget
from .models import *

class PrinterForm(ModelForm):
    class Meta:
        model = Printer
        fields = ['name', 'action_on_failure', 'tools_off_on_pause', 'bed_off_on_pause',
                  'detective_sensitivity', 'retract_on_pause', 'lift_z_on_pause']
        widgets = {
            'action_on_failure': CustomRadioSelectWidget(choices=Printer.ACTION_ON_FAILURE),
        }


class UserPreferencesForm(ModelForm):
    telegram_chat_id = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_country_code', 'phone_number', 'pushbullet_access_token',
                  'telegram_chat_id', 'notify_on_done', 'notify_on_canceled', 'account_notification_by_email',
                  'print_notification_by_email', 'print_notification_by_pushbullet', 'print_notification_by_telegram',
                  'alert_by_sms', 'alert_by_email', 'discord_webhook', 'print_notification_by_discord']
        widgets = {
            'phone_country_code': PhoneCountryCodeWidget()
        }

    def clean_phone_country_code(self):
        phone_country_code = self.cleaned_data['phone_country_code']
        if phone_country_code and not phone_country_code.startswith('+'):
            phone_country_code = '+' + phone_country_code
        return phone_country_code

    def clean(self):
        data = self.cleaned_data

        phone_number = (data['phone_country_code'] or '') + \
            (data['phone_number'] or '')

        if data['phone_country_code'] and data['phone_number']:
            phone_number = data['phone_country_code'] + data['phone_number']
            try:
                phone_number = phonenumbers.parse(phone_number, None)
                if not phonenumbers.is_valid_number(phone_number):
                    self.add_error('phone_number', 'Invalid phone number')
            except phonenumbers.NumberParseException as e:
                self.add_error('phone_number', e)

        if data['pushbullet_access_token']:
            pushbullet_access_token = data['pushbullet_access_token']
            try:
                Pushbullet(pushbullet_access_token)
            except PushbulletError:
                self.add_error('pushbullet_access_token',
                               'Invalid pushbullet access token.')

        data['telegram_chat_id'] = data['telegram_chat_id'] if data['telegram_chat_id'] else None

class SharedResourceForm(ModelForm):
    shared = BooleanField(required=True)

    class Meta:
        model = SharedResource
        fields = ['share_token']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        shared = bool(self.instance.share_token)
