from django.core.exceptions import ValidationError
from django.conf import settings
import json
import hashlib
import hmac
from time import time

# See https://core.telegram.org/widgets/login#checking-authorization for more information
# on how this auth validation works.
def validate_telegram_login(auth_dict):
    if not auth_dict:
        return

    auth_dict = json.loads(auth_dict)
    verification = auth_dict.pop('hash')

    data_check_str = '\n'.join(
        "{}={}".format(key, auth_dict[key]) for (key) in sorted(auth_dict)
    )
    auth_date = auth_dict['auth_date']

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    digest = hmac.new(
        secret_key,
        msg=data_check_str.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    one_hour_in_seconds = 3600
    valid = (int(time()) - int(auth_date) < one_hour_in_seconds) and hmac.compare_digest(digest, verification)
    if not valid:
        raise ValidationError('Invalid telegram login')
