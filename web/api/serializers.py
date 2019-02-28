from rest_framework import serializers

from app.models import *

class PrinterPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterPrediction
        fields = '__all__'

class PrinterSerializer(serializers.ModelSerializer):
    pic = serializers.DictField(read_only=True)
    status = serializers.DictField(read_only=True)
    printerprediction = PrinterPredictionSerializer(read_only=True)

    class Meta:
        model = Printer
        fields = ('name', 'pic', 'status', 'current_print_filename', 'current_print_started_at', 'current_print_alerted_at', 'alert_acknowledged_at', 'printerprediction')
