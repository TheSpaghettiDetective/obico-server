from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.relations import PrimaryKeyRelatedField
from django.conf import settings
import re
from django.utils.timezone import now
from pushbullet import Pushbullet, PushbulletError
import phonenumbers
import json

from app.models import (
    User, Print, Printer, GCodeFile, PrintShotFeedback, PrinterPrediction, MobileDevice, OneTimeVerificationCode,
    SharedResource, OctoPrintTunnel, calc_normalized_p,
    NotificationSetting, PrinterEvent, GCodeFolder, FirstLayerInspection, FirstLayerInspectionImage,
)

from notifications.handlers import handler


def int_with_default(v, default):
    try:
        return int(v)
    except ValueError:
        return default


class UserSerializer(serializers.ModelSerializer):
    is_primary_email_verified = serializers.ReadOnlyField()
    is_dh_unlimited = serializers.ReadOnlyField()

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'syndicate')
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'consented_at': {'read_only': True},
            'is_pro': {'read_only': True},
            'dh_balance': {'read_only': True},
            'unsub_token': {'read_only': True},
        }


class PrintShotFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintShotFeedback
        fields = ('id', 'print_id', 'image_url', 'answer', 'answered_at')
        read_only_fields = ('id', 'url', 'image_url', 'answered_at')

    def update(self, instance, validated_data):
        if 'answer' in validated_data:
            instance.answered_at = now()

        return super().update(instance, validated_data)


class BasePrinterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Printer
        fields = ('id', 'name', 'created_at', 'action_on_failure',
                  'watching_enabled', 'not_watching_reason',
                  'tools_off_on_pause', 'bed_off_on_pause', 'retract_on_pause',
                  'lift_z_on_pause', 'detective_sensitivity',
                  'min_timelapse_secs_on_finish', 'min_timelapse_secs_on_cancel',
                  'auth_token', 'archived_at', 'agent_name', 'agent_version',)

        read_only_fields = ('created_at', 'not_watching_reason', 'auth_token', 'archived_at',)


class BaseGCodeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GCodeFile
        fields = '__all__'
        read_only_fields = ('user', 'resident_printer')


class FirstLayerInspectionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FirstLayerInspectionImage
        fields = '__all__'


class FirstLayerInspectionSerializer(serializers.ModelSerializer):
    images = FirstLayerInspectionImageSerializer(many=True, read_only=True, source='firstlayerinspectionimage_set')

    class Meta:
        model = FirstLayerInspection
        fields = '__all__'


class BasePrintSerializer(serializers.ModelSerializer):
    ended_at = serializers.DateTimeField(read_only=True)
    printer = BasePrinterSerializer(many=False, read_only=True)
    g_code_file = BaseGCodeFileSerializer(many=False, read_only=True)

    class Meta:
        model = Print
        fields = ('id', 'printer', 'g_code_file', 'filename', 'started_at', 'ended_at', 'finished_at',
                  'cancelled_at', 'uploaded_at', 'alerted_at',
                  'alert_acknowledged_at', 'alert_muted_at', 'paused_at',
                  'video_url', 'tagged_video_url', 'poster_url', 'alert_overwrite', 'filament_used', 'print_time',
                  'access_consented_at', 'video_archived_at', 'need_alert_overwrite', 'need_print_shot_feedback')
        read_only_fields = (
            'id', 'g_code_file', 'filename', 'started_at', 'ended_at', 'finished_at',
            'cancelled_at', 'uploaded_at', 'alerted_at',
            'alert_acknowledged_at', 'alert_muted_at', 'paused_at',
            'video_url', 'tagged_video_url', 'poster_url',
            'video_archived_at', 'need_alert_overwrite', 'need_print_shot_feedback')

    def get_prediction_json_url(self, obj: Print) -> str:
        return reverse('Print-prediction-json', kwargs={'pk': obj.pk})


class PrintSerializer(BasePrintSerializer):
    printshotfeedback_set = PrintShotFeedbackSerializer(many=True, read_only=True)
    prediction_json_url = serializers.SerializerMethodField()
    firstlayerinspection_set = FirstLayerInspectionSerializer(many=True, read_only=True)

    class Meta:
        model = Print
        fields = BasePrintSerializer.Meta.fields + ('printer', 'prediction_json_url', 'printshotfeedback_set', 'firstlayerinspection_set',)
        read_only_fields = BasePrintSerializer.Meta.read_only_fields + ('printer', 'prediction_json_url', 'printshotfeedback_set', 'firstlayerinspection_set',)

    def get_prediction_json_url(self, obj: Print) -> str:
        return reverse('Print-prediction-json', kwargs={'pk': obj.pk})


class PrinterSerializer(BasePrinterSerializer):
    pic = serializers.DictField(read_only=True)
    status = serializers.DictField(read_only=True)
    settings = serializers.DictField(read_only=True)
    normalized_p = serializers.SerializerMethodField()
    current_print = BasePrintSerializer(read_only=True)

    class Meta:
        model = Printer
        fields = BasePrinterSerializer.Meta.fields + ('pic', 'status', 'settings', 'current_print','normalized_p',)
        read_only_fields = BasePrinterSerializer.Meta.read_only_fields + ('pic', 'status', 'settings', 'current_print', 'normalized_p',)

    def get_normalized_p(self, obj: Printer) -> float:
        return calc_normalized_p(obj.detective_sensitivity, obj.printerprediction) if hasattr(obj, 'printerprediction') else 0


class BaseGCodeFolderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    g_code_folder_count = serializers.IntegerField(read_only=True)
    g_code_file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = GCodeFolder
        fields = '__all__'
        read_only_fields = ('user', 'safe_name')


class GCodeFolderDeSerializer(BaseGCodeFolderSerializer):
    parent_folder = PrimaryKeyRelatedField(queryset=GCodeFolder.objects, allow_null=True, required=False)

    def validate_parent_folder(self, parent_folder):
        if parent_folder is not None and self.context['request'].user != parent_folder.user:
            raise serializers.ValidationError('Parent folder does not exist')
        return parent_folder

    def validate(self, attrs):
        attrs = super().validate(attrs)

        user = self.context['request'].user
        if 'name' in attrs:   # safe_name should always be updated when name is
            safe_name = re.sub(r'[^\w\.]', '_', attrs['name'])
            attrs['safe_name'] = safe_name
        elif self.instance:
            safe_name = self.instance.safe_name

        if 'parent_folder' in attrs:
            parent_folder = attrs.get('parent_folder')
            if parent_folder is None: # '?parent_folder='
                existing = GCodeFolder.objects.filter(user=user, parent_folder__isnull=True, safe_name=safe_name).first()
            else:
                existing = GCodeFolder.objects.filter(user=user, parent_folder=parent_folder, safe_name=safe_name).first()

            if existing and self.instance and existing.id != self.instance.id:
                raise serializers.ValidationError({'name': f'Already existed.'})

        return attrs

class GCodeFolderSerializer(BaseGCodeFolderSerializer):
    parent_folder = BaseGCodeFolderSerializer()


class GCodeFileDeSerializer(serializers.ModelSerializer):
    parent_folder = PrimaryKeyRelatedField(queryset=GCodeFolder.objects, allow_null=True, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GCodeFile
        fields = '__all__'
        read_only_fields = ('user', 'resident_printer', 'safe_filename')

    def validate_parent_folder(self, parent_folder):
        if parent_folder is not None and self.context['request'].user != parent_folder.user:
            raise serializers.ValidationError('Parent folder does not exist')
        return parent_folder

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if 'filename' in attrs: # safe_filename should always be updated when filename is
            safe_filename = re.sub(r'[^\w\.]', '_', attrs['filename'])
            attrs['safe_filename'] = safe_filename

        return attrs


class GCodeFileSerializer(BaseGCodeFileSerializer):
    parent_folder = BaseGCodeFolderSerializer()
    print_set = BasePrintSerializer(many=True, read_only=True)


class MobileDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileDevice
        fields = '__all__'
        read_only_fields = ('user', 'deactivated_at')


class OneTimeVerificationCodeSerializer(serializers.ModelSerializer):
    printer = PrinterSerializer(many=False, read_only=True)

    class Meta:
        model = OneTimeVerificationCode
        fields = ('id', 'printer', 'code', 'expired_at', 'verified_at',)


class SharedResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedResource
        fields = ('id', 'printer_id', 'share_token',)


class OctoPrintTunnelSerializer(serializers.ModelSerializer):
    target_printer_id = serializers.IntegerField(required=True, write_only=True)
    app_name = serializers.CharField(max_length=64, required=True, write_only=True)

    printer = PrinterSerializer(many=False, required=False)

    class Meta:
        model = OctoPrintTunnel
        fields = (
            'id', 'app', 'printer', 'subdomain_code', 'port', 'basicauth_username',
            'created_at', 'updated_at', 'app_name', 'target_printer_id'
        )
        read_only_fields = (
            'id', 'app', 'printer', 'subdomain_code', 'port', 'basicauth_username',
            'created_at', 'updated_at',
        )


class NotificationSettingSerializer(serializers.ModelSerializer):
    config = serializers.DictField(required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = NotificationSetting
        fields = (
            'id', 'user', 'created_at', 'updated_at',
            'name', 'config', 'enabled',
            'notify_on_failure_alert',
            'notify_on_print_done',
            'notify_on_print_cancelled',
            'notify_on_filament_change',
            'notify_on_heater_status',
            'notify_on_print_start',
            'notify_on_print_pause',
            'notify_on_print_resume',
        )

        read_only_fields = (
            'id', 'user', 'created_at', 'updated_at',
        )

    def validate_name(self, name):
        name = name.strip()
        plugin = handler.notification_plugin_by_name(name)
        if not plugin:
            raise Exception(f'Notification Plugin "{name}" is not loaded')

        return name

    def validate(self, data):
        name = data['name']
        plugin = handler.notification_plugin_by_name(name)
        if not plugin:
            raise Exception(f'Notification Plugin "{name}" is not loaded')

        need_to_validate_config = (not self.partial) or 'config' in data
        if need_to_validate_config:
            try:
                data['config'] = plugin.instance.validate_config(data['config'])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({'config': e.detail})

        return data

    def save(self):
        config = self.validated_data.pop('config', None)
        if config:
            self.validated_data['config_json'] = json.dumps(config)

        # HACK: For some reason sqlite will set created_at to None on a PATCH call and results in an exception. Force it now()
        if settings.DATABASES.get('default', {}).get('ENGINE') == 'django.db.backends.sqlite3':
            return super().save(user=self.context['request'].user, created_at=now(), updated_at=now())

        return super().save()


class PrinterEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrinterEvent
        fields = '__all__'
        read_only_fields = ('printer', 'print')


# For public APIs

class PublicPrinterSerializer(serializers.ModelSerializer):
    pic = serializers.DictField(read_only=True)

    class Meta:
        model = Printer
        fields = ('name', 'pic', 'settings')


class VerifyCodeInputSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64, required=True)