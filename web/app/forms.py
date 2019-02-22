from django.db import models
from django.forms import ModelForm

from .widgets import RadioSelectWidget

from .models import *

class PrinterForm(ModelForm):
    class Meta:
        model = Printer
        fields = ['name', 'action_on_failure', 'tools_off_on_pause', 'bed_off_on_pause']
        widgets = {
            'action_on_failure': RadioSelectWidget(choices=Printer.ACTION_ON_FAILURE),
        }

class UserPrefernecesForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
