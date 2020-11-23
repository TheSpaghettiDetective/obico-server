from firebase_admin.messaging import Message, send, AndroidConfig, APNSConfig, APNSPayload, Aps
import firebase_admin
from .utils import shortform_duration

from app.models import calc_normalized_p, MobileDevice

default_app = firebase_admin.initialize_app()

def send_print_progress(printer):
    data = dict(
        type='printProgress',
        printId=str(printer.current_print.id),
        title='',
        body=printer.current_print.filename,
        picUrl='',
    )

    completion = printer.status.get('progress', {}).get('completion')
    data['completion'] = str(round(completion or 0))
    data['title'] += f'{data["completion"] if completion else "-"}%'

    progress = printer.status.get('progress')
    if progress:
        seconds_past = progress.get('printTime', 0)
        seconds_left = progress.get('printTimeLeft', 0)
        data['title'] += f' | {shortform_duration(seconds_left)}/{shortform_duration(seconds_left + seconds_past)}'

    if printer.not_watching_reason():
        data['title'] += ' | 😴'
    else:
        p = calc_normalized_p(printer.detective_sensitivity, printer.printerprediction)
        if p < 0.33:
            data['title'] += ' | 😀'
        elif p < 0.66:
            data['title'] += ' | 😐'
        else:
            data['title'] += ' | 😱'

    if printer.pic:
        data['picUrl'] = printer.pic.get('img_url', '')

    for mobile_device in MobileDevice.objects.filter(user=printer.user):
        send_to_device(data, mobile_device.device_token)

def send_to_device(msg, device_token):
    message = Message(
            data=msg,
            android=AndroidConfig(priority='high'),
            apns=APNSConfig(headers={'apns-push-type': 'background', 'apns-priority': '5'}, payload=APNSPayload(aps=Aps(content_available=True))),
            token=device_token)
    return send(message)

if __name__ == '__main__':
    import json
    import sys
    with open(sys.argv[1], 'r') as json_file:
        msg = json.load(json_file)
    print(send_to_device(device_token=sys.argv[2],msg=msg))
