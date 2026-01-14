from datetime import datetime, date
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from app.models import User
from .models import JusPrinAICredit


def consume_credit_for_pipeline(user_id: int) -> dict:
    """Atomically check and consume 1 credit for an AI pipeline call.

    This should be called before every LLM pipeline execution.
    Combines checking and deducting in a single atomic operation.

    Args:
        user_id: User ID

    Returns:
        Dictionary with operation result:
        {
            'success': bool,
            'used_credits': int,
            'monthly_limit': int,
            'message': str
        }
    """
    with transaction.atomic():
        ai_credit, created = JusPrinAICredit.objects.get_or_create(user_id=user_id)
        monthly_limit = ai_credit.ai_credit_free_monthly_quota

        # If quota is -1 (unlimited), allow usage
        if monthly_limit == -1:
            return {
                'success': True,
                'used_credits': 0,
                'monthly_limit': -1,  # -1 indicates unlimited
                'message': _('Unlimited usage allowed')
            }

        # Check if we would exceed the limit
        if ai_credit.ai_credit_used_current_month >= monthly_limit:
            return {
                'success': False,
                'used_credits': ai_credit.ai_credit_used_current_month,
                'monthly_limit': monthly_limit,
                'message': _('Monthly AI credit limit exceeded')
            }

        # Consume the credit
        ai_credit.ai_credit_used_current_month += 1
        ai_credit.save()

        return {
            'success': True,
            'used_credits': ai_credit.ai_credit_used_current_month,
            'monthly_limit': monthly_limit,
            'message': _('Credit consumed successfully')
        }



def get_credits_info(user_id: int) -> dict:
    """Get comprehensive credits information for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary with all credit information
    """
    ai_credit, created = JusPrinAICredit.objects.get_or_create(user_id=user_id)
    monthly_limit = ai_credit.ai_credit_free_monthly_quota
    used = ai_credit.ai_credit_used_current_month

    return {
        'monthly_limit': monthly_limit,
        'used_credits': used,
        'credits_enabled': monthly_limit != -1,
        'can_use_ai': monthly_limit == -1 or used < monthly_limit
    }