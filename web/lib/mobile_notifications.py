from firebase_admin import messaging
import firebase_admin

default_app = firebase_admin.initialize_app()

def send_to_device(registration_token, msg):
    message = messaging.Message(data=msg, token=registration_token)
    return messaging.send(message)

if __name__ == "__main__":
    import json
    import sys
    with open(sys.argv[1], 'r') as json_file:
        msg = json.load(json_file)
    print(send_to_device(registration_token=sys.argv[2],msg=msg))
