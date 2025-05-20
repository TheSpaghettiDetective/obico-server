from rest_framework import serializers

from .models import JusPrinChat

class JusPrinChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = JusPrinChat
        exclude = ['user']
