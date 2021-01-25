import requests
import io

class PushoverException(Exception):
    pass

class PushoverClient(object):
    API_URL = "https://api.pushover.net/1/messages.json"

    def __init__(self, app_key, user_key):
        self.app_key = app_key
        self.user_key = user_key

    # message and title should be strings, attachment should be a file-like object
    def push_notification(self, message, title = None, attachment = None):
        if len(message) > 1024:
            raise PushoverException("Maximum message size of 1024 characters exceeded!")
        
        if title and len(title) > 250:
            raise PushoverException("Maximum title size of 250 characters exceeded!")


        payload = {
            "token": self.app_key,
            "user": self.user_key,
            "message": message
        }

        if title:
            payload["title"] = title

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

        req = requests.post(self.API_URL, data=payload, files = files)

        if req.status_code != requests.codes.ok:
            raise req.raise_for_status

        return True