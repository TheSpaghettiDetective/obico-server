from datetime import datetime, date
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from app.models import User
from .models import JusPrinAICredit


def _get_current_month_start() -> date:
    """Get the start date of the current month.

    Returns:
        First day of current month
    """
    now = timezone.now().date()
    return date(now.year, now.month, 1)


def get_monthly_free_credits_limit(user_id: int) -> int:
    """Get the monthly free credits limit for a user.

    Args:
        user_id: User ID

    Returns:
        Number of free credits per month, or -1 if unlimited
    """
    return ai_credit.ai_credit_free_monthly_quota


def get_used_credits(user_id: int) -> int:
    """Get used AI credits for the current month.

    Args:
        user_id: User ID

    Returns:
        Number of used credits for this month
    """
    return ai_credit.ai_credit_used_current_month


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
    try:
        with transaction.atomic():

            monthly_limit = ai_credit.ai_credit_free_monthly_quota

            # If quota is -1 (unlimited), allow usage
            if monthly_limit == -1:
                return {
                    'success': True,
                    'used_credits': 0,
                    'monthly_limit': -1,  # -1 indicates unlimited
                    'message': 'Unlimited usage allowed'
                }

            # If quota is 0, block usage
            if monthly_limit <= 0:
                return {
                    'success': False,
                    'used_credits': ai_credit.ai_credit_used_current_month,
                    'monthly_limit': monthly_limit,
                    'message': 'AI credits disabled - usage blocked'
                }

            # Check if we would exceed the limit
            if ai_credit.ai_credit_used_current_month >= monthly_limit:
                return {
                    'success': False,
                    'used_credits': ai_credit.ai_credit_used_current_month,
                    'monthly_limit': monthly_limit,
                    'message': 'Monthly AI credit limit exceeded'
                }

            # Consume the credit
            ai_credit.ai_credit_used_current_month += 1
            ai_credit.save()

            return {
                'success': True,
                'used_credits': ai_credit.ai_credit_used_current_month,
                'monthly_limit': monthly_limit,
                'message': 'Credit consumed successfully'
            }

    except User.DoesNotExist:
        return {
            'success': False,
            'used_credits': 0,
            'monthly_limit': 0,
            'message': 'User not found'
        }
    except Exception as e:
        return {
            'success': False,
            'used_credits': 0,
            'monthly_limit': 0,
            'message': f'Error processing credit: {str(e)}'
        }


def reset_monthly_credits(user_id: int) -> dict:
    """Reset user's monthly credits (for admin/testing purposes).

    Args:
        user_id: User ID

    Returns:
        Dictionary with reset result
    """
    try:
        ai_credit.ai_credit_used_current_month = 0
        ai_credit.save()

        return {
            'success': True,
            'used_credits': 0,
            'monthly_limit': ai_credit.ai_credit_free_monthly_quota,
            'message': 'Monthly credits reset successfully'
        }

    except User.DoesNotExist:
        return {
            'success': False,
            'used_credits': 0,
            'monthly_limit': 0,
            'message': 'User not found'
        }
    except Exception as e:
        return {
            'success': False,
            'used_credits': 0,
            'monthly_limit': 0,
            'message': f'Error resetting credits: {str(e)}'
        }


def get_credits_info(user_id: int) -> dict:
    """Get comprehensive credits information for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary with all credit information
    """
    try:

        monthly_limit = ai_credit.ai_credit_free_monthly_quota
        used = ai_credit.ai_credit_used_current_month

        return {
            'monthly_limit': monthly_limit,
            'used_credits': used,
            'credits_enabled': monthly_limit != -1,
            'can_use_ai': monthly_limit == -1 or used < monthly_limit
        }

    except User.DoesNotExist:
        return {
            'monthly_limit': 0,
            'used_credits': 0,
            'credits_enabled': False,
            'can_use_ai': False
        }
    except Exception:
        return {
            'monthly_limit': 0,
            'used_credits': 0,
            'credits_enabled': False,
            'can_use_ai': False
        }