from .models import *

from app import ma

class PrintSchema(ma.ModelSchema):
    class Meta:
        model = Print

class PrinterSchema(ma.ModelSchema):
    class Meta:
        model = Printer
