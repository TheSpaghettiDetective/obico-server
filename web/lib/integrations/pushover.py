import requests
import io
from django.conf import settings
from enum import IntEnum

class PushoverException(Exception):
    pass

class PushoverPriority(IntEnum) :
    # See https://pushover.net/api#priority for more details on pushover notification priority
    LOWEST = -2 # Don't show any notification
    LOW = -1 # Show a quiet (non-alerting) notification
    NORMAL = 0 # Show a normal notification that respects a user's quiet hours
    HIGH = 1 # Show a high-priority notification that bypasses a user's quiet hours
    EMERGENCY = 2 # Show a high-priority notification that requires user confirmation

# message and title should be strings, attachment should be a file-like object
def pushover_notification(user_key, message, title = None, attachment = None, priority = None):
    API_URL = "https://api.pushover.net/1/messages.json"
    RETRY = 60 # seconds
    EXPIRE = 120 # seconds

    if len(message) > 1024:
        raise PushoverException("Maximum message size of 1024 characters exceeded!")

    if title and len(title) > 250:
        raise PushoverException("Maximum title size of 250 characters exceeded!")


    payload = {
        "token": os.environ.get('PUSHOVER_APP_TOKEN'),
        "user": user_key,
        "message": message
    }

    if title:
        payload["title"] = title

    if priority:
        payload["priority"] = int(priority)

        if priority == PushoverPriority.EMERGENCY:
            # retry every RETRY seconds for EXPIRE seconds total
            payload["retry"] = RETRY
            payload["expire"] = EXPIRE

    files = None
    if attachment:
        if attachment is bytes:
            files = {
                "attachment": io.BytesIO(attachment)
            }
        else:
            files = {
                "attachment": attachment
            }

    req = requests.post(API_URL, data=payload, files = files)
    req.raise_for_status()

    return True
