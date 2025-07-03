from rest_framework import serializers
from datetime import date, datetime
from calendar import monthrange
from django.conf import settings
import requests
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import JusPrinChat, JusPrinAICredit

User = get_user_model()

class JusPrinChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = JusPrinChat
        exclude = ['user']

class JusPrinAICreditSerializer(serializers.ModelSerializer):
    used_credits = serializers.SerializerMethodField()
    available_credits = serializers.SerializerMethodField()
    credits_enabled = serializers.SerializerMethodField()
    can_use_ai = serializers.SerializerMethodField()
    reset_date = serializers.SerializerMethodField()

    class Meta:
        model = JusPrinAICredit
        fields = [
            'ai_credit_free_monthly_quota',
            'ai_credit_used_current_month',
            'used_credits',
            'available_credits',
            'credits_enabled',
            'can_use_ai',
            'reset_date',
            'created_at',
            'updated_at'
        ]

    def get_used_credits(self, obj):
        return obj.ai_credit_used_current_month

    def get_available_credits(self, obj):
        if obj.ai_credit_free_monthly_quota == -1:
            return -1  # Unlimited
        return max(0, obj.ai_credit_free_monthly_quota - obj.ai_credit_used_current_month)

    def get_credits_enabled(self, obj):
        return obj.ai_credit_free_monthly_quota != -1

    def get_can_use_ai(self, obj):
        if obj.ai_credit_free_monthly_quota == -1:
            return True  # Unlimited
        return obj.ai_credit_used_current_month < obj.ai_credit_free_monthly_quota

    def get_reset_date(self, obj):
        """Get the next month's first day as reset date"""
        today = date.today()
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        return next_month.strftime("%B 1st")

class UserAICreditInfoSerializer(serializers.Serializer):
    """Serializer for user AI credit information with user details"""
    user_info = serializers.SerializerMethodField()
    credits = serializers.SerializerMethodField()

    def _get_obico_subscription_data(self, user):
        """Get subscription data from obico API if IS_ENT is true"""
        try:
            # Check if this is an enterprise installation
            if not getattr(settings, 'IS_ENT', False):
                return None

            # Make internal API call to get subscription data
            # We need to make this call as the authenticated user
            from django.test import Client
            from django.contrib.auth import get_user_model

            client = Client()
            client.force_login(user)

            # Try to get subscription data
            try:
                response = client.get('/ent/api/subscriptions/active/')
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                # If we can't get subscription data, log it but don't fail
                import logging
                logging.warning(f"Failed to get subscription data for user {user.id}: {e}")

        except Exception as e:
            # If anything goes wrong with subscription API, log it but don't fail
            import logging
            logging.warning(f"Error checking subscription for user {user.id}: {e}")

        return None

    def get_user_info(self, user):
        user_info = {
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'username': user.username,
            'has_active_subscription': False,
            'subscription_plan': None
        }

        # If IS_ENT is true, get subscription data from obico API
        subscription_data = self._get_obico_subscription_data(user)
        if subscription_data:
            # Update user info with subscription data
            if subscription_data.get('subscription'):
                sub = subscription_data['subscription']
                user_info['has_active_subscription'] = True
                user_info['subscription_plan'] = sub.get('plan_id', 'Pro')

                # Use subscription user data if available
                if sub.get('user'):
                    sub_user = sub['user']
                    user_info['name'] = sub_user.get('first_name', '') + ' ' + sub_user.get('last_name', '')
                    user_info['name'] = user_info['name'].strip() or sub_user.get('email', user.email)
                    user_info['email'] = sub_user.get('email', user.email)

        return user_info

    def get_credits(self, user):
        try:
            ai_credit = JusPrinAICredit.objects.get(user=user)
            serializer = JusPrinAICreditSerializer(ai_credit)
            data = serializer.data

            # Transform data to match Vue component expectations
            credits_data = {
                'total': ai_credit.ai_credit_free_monthly_quota if ai_credit.ai_credit_free_monthly_quota != -1 else 999999,
                'used': ai_credit.ai_credit_used_current_month,
                'available': data['available_credits'] if data['available_credits'] != -1 else 999999,
                'monthly_limit': ai_credit.ai_credit_free_monthly_quota,
                'credits_enabled': data['credits_enabled'],
                'can_use_ai': data['can_use_ai'],
                'reset_date': data['reset_date'],
                'purchased': 0  # For future use
            }

            # If user has active subscription, they might have different credit limits
            subscription_data = self._get_obico_subscription_data(user)
            if subscription_data and subscription_data.get('subscription'):
                # Pro users might have unlimited credits or higher limits
                # This could be expanded based on subscription plan
                plan_id = subscription_data['subscription'].get('plan_id', '')
                if 'pro' in plan_id.lower() or 'unlimited' in plan_id.lower():
                    # Pro users could have higher limits - adjust as needed
                    pass

            return credits_data

        except JusPrinAICredit.DoesNotExist:
            # Return default values if no AI credit record exists
            return {
                'total': 0,
                'used': 0,
                'available': 0,
                'monthly_limit': 0,
                'credits_enabled': False,
                'can_use_ai': False,
                'reset_date': 'Next month',
                'purchased': 0
            }


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for JusPrin API"""
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'first_name', 'last_name']

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class JusPrinMeSerializer(serializers.Serializer):
    """Consolidated serializer for /jusprin/api/me/ endpoint"""
    user = serializers.SerializerMethodField()
    ai_credits = serializers.SerializerMethodField()

    def _get_enterprise_ai_credits(self, user):
        """Get AI credits from enterprise API if IS_ENT is true"""
        try:
            # Check if this is an enterprise installation
            if not getattr(settings, 'IS_ENT', False):
                return None

            # Make internal API call to get AI credits data
            from django.test import Client

            client = Client()
            client.force_login(user)

            # Try to get AI credits data from enterprise API
            try:
                response = client.get('/jusprin/api/ai_credits/user_info/')
                if response.status_code == 200:
                    data = response.json()
                    # Return just the credits portion
                    return data.get('credits')
            except Exception as e:
                # If we can't get enterprise data, log it but don't fail
                import logging
                logging.warning(f"Failed to get enterprise AI credits for user {user.id}: {e}")

        except Exception as e:
            # If anything goes wrong with enterprise API, log it but don't fail
            import logging
            logging.warning(f"Error checking enterprise AI credits for user {user.id}: {e}")

        return None

    def get_user(self, user):
        serializer = UserSerializer(user)
        return serializer.data

    def get_ai_credits(self, user):
        # First try to get enterprise AI credits if IS_ENT is true
        enterprise_credits = self._get_enterprise_ai_credits(user)
        if enterprise_credits:
            return enterprise_credits

        # Fallback to local AI credits
        try:
            ai_credit = JusPrinAICredit.objects.get(user=user)
            serializer = JusPrinAICreditSerializer(ai_credit)
            data = serializer.data

            # Transform data to match Vue component expectations
            return {
                'total': ai_credit.ai_credit_free_monthly_quota if ai_credit.ai_credit_free_monthly_quota != -1 else 999999,
                'used': ai_credit.ai_credit_used_current_month,
                'available': data['available_credits'] if data['available_credits'] != -1 else 999999,
                'monthly_limit': ai_credit.ai_credit_free_monthly_quota,
                'credits_enabled': data['credits_enabled'],
                'can_use_ai': data['can_use_ai'],
                'reset_date': data['reset_date'],
                'purchased': 0
            }

        except JusPrinAICredit.DoesNotExist:
            # Return default values if no AI credit record exists
            return {
                'total': 50,  # Default free tier
                'used': 0,
                'available': 50,
                'monthly_limit': 50,
                'credits_enabled': True,
                'can_use_ai': True,
                'reset_date': 'Next month',
                'purchased': 0
            }
