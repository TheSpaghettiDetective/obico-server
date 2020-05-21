from rest_framework import serializers

from app.models import *


class PrinterPredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrinterPrediction
        fields = '__all__'


class PrintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Print
        fields = '__all__'


class PrinterSerializer(serializers.ModelSerializer):
    pic = serializers.DictField(read_only=True)
    status = serializers.DictField(read_only=True)
    settings = serializers.DictField(read_only=True)
    printerprediction = PrinterPredictionSerializer(read_only=True)
    current_print = PrintSerializer(read_only=True)

    class Meta:
        model = Printer
        fields = ('name', 'action_on_failure', 'watching', 'should_watch', 'pic', 'status', 'settings', 'current_print', 'printerprediction')


class GCodeFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GCodeFile
        fields = '__all__'
