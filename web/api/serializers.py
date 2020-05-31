from rest_framework import serializers
from django.utils.timezone import now

from app.models import *
from app.models import PrintShotFeedback


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


class PrintShotFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintShotFeedback
        fields = ('id', 'print_id', 'image_url', 'answer', 'answered_at')
        read_only_fields = ('id', 'url', 'image_url', 'answered_at')

    def update(self, instance, validated_data):
        if 'answer' in validated_data:
            if validated_data['answer'] != PrintShotFeedback.UNANSWERED:
                instance.answered_at = now()
            else:
                instance.answered_at = None

        return super().update(instance, validated_data)
