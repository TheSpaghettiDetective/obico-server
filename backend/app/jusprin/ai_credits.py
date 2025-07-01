from datetime import datetime
from django.conf import settings
from lib.cache import REDIS
from app.models import User


def _get_current_month_key(user_id: int) -> str:
    """Generate Redis key for current month's AI credits.

    Args:
        user_id: User ID

    Returns:
        Redis key string for current month
    """
    now = datetime.now()
    return f'jusprin:ai_credits:{user_id}:{now.year}:{now.month:02d}'


def get_monthly_free_credits_limit() -> int:
    """Get the monthly free credits limit from Django settings.

    Returns:
        Number of free credits per month, or 0 if not configured
    """
    limit = settings.JUSPRIN_FREE_CREDITS_PER_MONTH
    if limit is None:
        return 0
    try:
        return int(limit)
    except (ValueError, TypeError):
        return 0





def get_used_credits(user_id: int) -> int:
    """Get used AI credits for the current month.

    Args:
        user_id: User ID

    Returns:
        Number of used credits for this month (0 when unlimited)
    """
    # If not configured, return 0 (no tracking)
    if settings.JUSPRIN_FREE_CREDITS_PER_MONTH is None:
        return 0

    key = _get_current_month_key(user_id)
    return int(REDIS.get(key) or 0)








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
    # If JUSPRIN_FREE_CREDITS_PER_MONTH is not set (None), allow unlimited usage
    if settings.JUSPRIN_FREE_CREDITS_PER_MONTH is None:
        return {
            'success': True,
            'used_credits': 0,
            'monthly_limit': -1,  # -1 indicates unlimited
            'message': 'Credits not configured - unlimited usage allowed'
        }

    monthly_limit = get_monthly_free_credits_limit()

    if monthly_limit <= 0:
        return {
            'success': False,
            'used_credits': 0,
            'monthly_limit': 0,
            'message': 'AI credits configured but set to 0 - usage blocked'
        }

    key = _get_current_month_key(user_id)

    # Atomic check and increment using Redis pipeline
    with REDIS.pipeline() as pipe:
        pipe.get(key)
        pipe.incrby(key, 1)
        # Set expiration for automatic monthly reset
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        expire_seconds = int((next_month - now).total_seconds()) + 86400  # +1 day buffer
        pipe.expire(key, expire_seconds)

        results = pipe.execute()
        old_used = int(results[0] or 0)
        new_used = int(results[1])

    # Check if operation exceeded the limit
    if new_used > monthly_limit:
        # Rollback the increment
        REDIS.decrby(key, 1)
        return {
            'success': False,
            'used_credits': old_used,
            'monthly_limit': monthly_limit,
            'message': 'Monthly AI credit limit exceeded'
        }

    return {
        'success': True,
        'used_credits': new_used,
        'monthly_limit': monthly_limit,
        'message': 'Credit consumed successfully'
    }


def reset_monthly_credits(user_id: int) -> dict:
    """Reset user's monthly credits (for admin/testing purposes).

    Args:
        user_id: User ID

    Returns:
        Dictionary with reset result
    """
    # If not configured, return unlimited status
    if settings.JUSPRIN_FREE_CREDITS_PER_MONTH is None:
        return {
            'success': True,
            'used_credits': 0,
            'monthly_limit': -1,  # -1 indicates unlimited
            'message': 'Credits not configured - unlimited usage allowed'
        }

    key = _get_current_month_key(user_id)
    REDIS.delete(key)

    monthly_limit = get_monthly_free_credits_limit()

    return {
        'success': True,
        'used_credits': 0,
        'monthly_limit': monthly_limit,
        'message': 'Monthly credits reset successfully'
    }


def get_credits_info(user_id: int) -> dict:
    """Get comprehensive credits information for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary with all credit information
    """
    # If not configured, return unlimited status
    if settings.JUSPRIN_FREE_CREDITS_PER_MONTH is None:
        return {
            'monthly_limit': -1,  # -1 indicates unlimited
            'used_credits': 0,
            'credits_enabled': False,  # Not enabled/configured
            'can_use_ai': True  # Always allowed when unlimited
        }

    monthly_limit = get_monthly_free_credits_limit()
    used = get_used_credits(user_id)

    return {
        'monthly_limit': monthly_limit,
        'used_credits': used,
        'credits_enabled': monthly_limit > 0,
        'can_use_ai': used < monthly_limit
    }