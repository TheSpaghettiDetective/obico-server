from rest_framework import serializers
from rest_framework.reverse import reverse
from django.utils.timezone import now

from app.models import User, Print, Printer, GCodeFile, PrintShotFeedback, MobileDevice, OneTimeVerificationCode
from app.models import calc_normalized_p


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'is_pro', 'dh_balance')


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
    prediction_json_url = serializers.SerializerMethodField()

    class Meta:
        model = Print
        fields = ('id', 'printer', 'filename', 'started_at', 'finished_at',
                  'cancelled_at', 'uploaded_at', 'alerted_at',
                  'alert_acknowledged_at', 'alert_muted_at', 'paused_at',
                  'video_url', 'tagged_video_url', 'poster_url',
                  'prediction_json_url', 'alert_overwrite',
                  'access_consented_at', 'printshotfeedback_set')
        read_only_fields = ('id', 'printer', 'printshotfeedback_set')

    def get_prediction_json_url(self, obj: Print) -> str:
        return reverse('Print-prediction-json', kwargs={'pk': obj.pk})


class PrinterSerializer(serializers.ModelSerializer):
    pic = serializers.DictField(read_only=True)
    status = serializers.DictField(read_only=True)
    settings = serializers.DictField(read_only=True)
    normalized_p = serializers.SerializerMethodField()
    current_print = PrintSerializer(read_only=True)

    class Meta:
        model = Printer
        fields = ('id', 'name', 'created_at', 'action_on_failure',
                  'watching_enabled', 'not_watching_reason',
                  'pic', 'status', 'settings', 'current_print',
                  'normalized_p', 'auth_token', 'archived_at')

    def get_normalized_p(self, obj: Printer) -> float:
        return calc_normalized_p(obj.detective_sensitivity,
                                 obj.printerprediction)


class GCodeFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GCodeFile
        fields = '__all__'


class MobileDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileDevice
        fields = '__all__'


class OneTimeVerificationCodeSerializer(serializers.ModelSerializer):
    printer = PrinterSerializer(many=False, read_only=True)

    class Meta:
        model = OneTimeVerificationCode
        fields = ('printer', 'code', 'expired_at',)


# For public APIs

class PublicPrinterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Printer
        fields = ('name', 'settings')
