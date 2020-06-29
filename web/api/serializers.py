from rest_framework import serializers
from django.utils.timezone import now

from app.models import *


class PrinterPredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrinterPrediction
        fields = '__all__'


class PrintShotFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintShotFeedback
        fields = ('id', 'print_id', 'image_url', 'answer', 'answered_at')
        read_only_fields = ('id', 'url', 'image_url', 'answered_at')

    def update(self, instance, validated_data):
        if 'answer' in validated_data:
            instance.answered_at = now()

        return super().update(instance, validated_data)


class PrintSerializer(serializers.ModelSerializer):
    printshotfeedback_set = PrintShotFeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = Print
        fields = ('id', 'printer', 'filename', 'started_at', 'finished_at', 'cancelled_at', 'uploaded_at', 'alerted_at', 'alert_acknowledged_at',
                  'alert_muted_at', 'paused_at', 'video_url', 'tagged_video_url', 'poster_url', 'prediction_json_url', 'alert_overwrite', 'access_consented_at', 'printshotfeedback_set')
        read_only_fields = ('id', 'printer', 'printshotfeedback_set')


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


# For public APIs

class PublicPrinterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Printer
        fields = ('name',)
