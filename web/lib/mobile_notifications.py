from firebase_admin.messaging import Message, send, AndroidConfig, APNSConfig, APNSPayload, Aps
import firebase_admin

default_app = firebase_admin.initialize_app()

def send_to_device(registration_token, msg):
    message = Message(
            data=msg,
            android=AndroidConfig(priority="high"),
            apns=APNSConfig(payload=APNSPayload(aps=Aps(content_available=True))),
            token=registration_token)
    return send(message)

if __name__ == "__main__":
    import json
    import sys
    with open(sys.argv[1], 'r') as json_file:
        msg = json.load(json_file)
    print(send_to_device(registration_token=sys.argv[2],msg=msg))
