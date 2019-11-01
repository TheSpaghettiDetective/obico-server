from lib.redis import *
from .models import UNLIMITED_DH

def detective_hour_processor(request):
    if request.user.is_authenticated:
        dh_balance = user_dh_balance_get(request.user.id)
        if dh_balance >= UNLIMITED_DH:
            return {'dh_balance': '\u221E'}
        else:
            return {'dh_balance': int(dh_balance)}
    else:
        return {}
