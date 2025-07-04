from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JusPrinChat, JusPrinAICredit

User = get_user_model()

class JusPrinChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = JusPrinChat
        exclude = ['user']

class JusPrinAICreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = JusPrinAICredit
        fields = [
            'user',
            'ai_credit_free_monthly_quota',
            'ai_credit_used_current_month',
            'created_at',
            'updated_at',
        ]

class JusPrinMeSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    ai_credits = JusPrinAICreditSerializer(read_only=True)

    def to_representation(self, instance):
        # instance is the user object
        data = super().to_representation(instance)
        data['user'] = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }
        try:
            ai_credit = JusPrinAICredit.objects.get(user=instance)
            data['ai_credits'] = JusPrinAICreditSerializer(ai_credit).data
        except JusPrinAICredit.DoesNotExist:
            data['ai_credits'] = None
        return data
