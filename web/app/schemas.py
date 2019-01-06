from .models import *

from app import ma

class DetectionSchema(ma.ModelSchema):
    class Meta:
        model = Detection
