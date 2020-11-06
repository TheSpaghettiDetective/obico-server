from rest_framework import serializers
from django.utils.timezone import now

from config import settings
from app.models import *


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
    normalized_p = serializers.SerializerMethodField()
    current_print = PrintSerializer(read_only=True)

    class Meta:
        model = Printer
        fields = ('id', 'name', 'created_at', 'action_on_failure', 'watching_enabled', 'should_watch', 'not_watching_reason', 'pic', 'status', 'settings', 'current_print', 'normalized_p', 'auth_token', 'archived_at')

    def get_normalized_p(self, obj):

        def scale(oldValue, oldMin, oldMax, newMin, newMax):
            newValue = (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin
            return min(newMax, max(newMin, newValue))

        pred = obj.printerprediction
        thresh_warning = (pred.rolling_mean_short - pred.rolling_mean_long) * settings.ROLLING_MEAN_SHORT_MULTIPLE
        thresh_warning = min(settings.THRESHOLD_HIGH, max(settings.THRESHOLD_LOW, thresh_warning))
        thresh_failure = thresh_warning * settings.ESCALATING_FACTOR

        p = (pred.ewm_mean - pred.rolling_mean_long) * obj.detective_sensitivity

        if p > thresh_failure:
            return scale(p, thresh_failure, thresh_failure*1.5, 2.0/3.0, 1.0)
        elif p > thresh_warning:
            return scale(p, thresh_warning, thresh_failure, 1.0/3.0, 2.0/3.0)
        else:
            return scale(p, 0, thresh_warning, 0, 1.0/3.0)

class GCodeFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GCodeFile
        fields = '__all__'


# For public APIs

class PublicPrinterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Printer
        fields = ('name', 'settings')
