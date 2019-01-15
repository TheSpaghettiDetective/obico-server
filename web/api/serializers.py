from rest_framework import serializers

from app.models import *

class PrintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Print
        fields = ('name', 'current_img_url', 'current_img_num', 'detection_score', 'finished_at',)
        

class PrinterSerializer(serializers.ModelSerializer):
    current_print = PrintSerializer()

    class Meta:
        model = Printer
        fields = ('name', 'current_print',)