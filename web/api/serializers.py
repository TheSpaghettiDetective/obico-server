from rest_framework import serializers

from app.models import *

class PrinterSerializer(serializers.ModelSerializer):
    pic = serializers.DictField(read_only=True)
    status = serializers.DictField(read_only=True)

    class Meta:
        model = Printer
        fields = ('name', 'pic', 'status',)