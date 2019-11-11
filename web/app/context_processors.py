from lib.redis import *
from app_ent.detective_hour_accounting import dh_is_unlimited

def detective_hour_processor(request):
    if request.user.is_authenticated:
        dh_balance = user_dh_balance_get(request.user.id)
        if dh_is_unlimited(dh_balance):
            return {'dh_balance': '\u221E'}
        else:
            return {'dh_balance': round(dh_balance)}
    else:
        return {}
