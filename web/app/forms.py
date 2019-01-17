from django.db import models
from django.forms import ModelForm

from .models import *

class PrinterForm(ModelForm):
    class Meta:
        model = Printer
        fields = ['name']