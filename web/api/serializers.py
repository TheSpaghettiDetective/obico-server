from rest_framework import serializers
from rest_framework.reverse import reverse
from django.utils.timezone import now

from app.models import User, Print, Printer, GCodeFile, PrintShotFeedback, MobileDevice, OneTimeVerificationCode
from app.models import calc_normalized_p

import phonenumbers


class UserSerializer(serializers.ModelSerializer):
    is_primary_email_verified = serializers.ReadOnlyField()

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions',)
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'consented_at': {'read_only': True},
            'is_pro': {'read_only': True},
            'dh_balance': {'read_only': True},
            'unsub_token': {'read_only': True},
        }

    def validate_phone_country_code(self, phone_country_code):
        if phone_country_code and not phone_country_code.startswith('+'):
            phone_country_code = '+' + phone_country_code
        return phone_country_code

    def validate(self, data):
        if 'phone_number' in data and 'phone_country_code' in data:
            if data['phone_country_code'] and data['phone_number']:
                phone_number = data['phone_country_code'] + data['phone_number']
                try:
                    phone_number = phonenumbers.parse(phone_number, None)
                    if not phonenumbers.is_valid_number(phone_number):
                        raise serializers.ValidationError({'phone_number': 'Invalid phone number'})
                except phonenumbers.NumberParseException:
                    raise serializers.ValidationError({'phone_number': 'Cannot parse phone number'})

        return data


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
                  'tools_off_on_pause', 'bed_off_on_pause', 'retract_on_pause',
                  'lift_z_on_pause', 'detective_sensitivity',
                  'pic', 'status', 'settings', 'current_print',
                  'normalized_p', 'auth_token', 'archived_at', 'service_token')

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
        fields = ('id', 'printer', 'code', 'expired_at', 'verified_at',)


# For public APIs

class PublicPrinterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Printer
        fields = ('name', 'settings')
