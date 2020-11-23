from firebase_admin.messaging import Message, send, AndroidConfig, APNSConfig, APNSPayload, Aps, UnregisteredError
import firebase_admin
from django.utils.timezone import now

from .utils import shortform_duration
from app.models import calc_normalized_p, MobileDevice

default_app = firebase_admin.initialize_app()

def send_failure_alert(printer, rotated_jpg_url, is_warning, print_paused):
    data = dict(
        type='failureAlert',
        title=f'Print {"is fishy" if is_warning else "may be failing"} {" | Paused" if print_paused else ""}',
        body=printer.current_print.filename,
        picUrl=rotated_jpg_url,
    )

    for mobile_device in MobileDevice.objects.filter(user=printer.user):
        send_to_device(data, mobile_device.device_token)

def send_print_event(_print, event_type):
    data = dict(
        type='printEvent',
        eventType=event_type,
        printId=str(_print.id),
        title=f"{event_type.replace('Print', '')} | {_print.printer.name}",
        body=_print.filename,
        picUrl='',
    )
    if _print.printer.pic:
        data['picUrl'] = _print.printer.pic.get('img_url', '')

    for mobile_device in MobileDevice.objects.filter(user=_print.user):
        send_to_device(data, mobile_device.device_token)

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
        data['title'] += ' | 💤'
    else:
        p = calc_normalized_p(printer.detective_sensitivity, printer.printerprediction)
        if p < 0.33:
            data['title'] += ' | ☀'
        elif p < 0.66:
            data['title'] += ' | ☁'
        else:
            data['title'] += ' | 🌧'

    if printer.pic:
        data['picUrl'] = printer.pic.get('img_url', '')

    for mobile_device in MobileDevice.objects.filter(user=printer.user):
        send_to_device(data, mobile_device.device_token)

def send_to_device(msg, device_token):
    try:
        message = Message(
            data=msg,
            android=AndroidConfig(priority='high'),
            apns=APNSConfig(headers={'apns-push-type': 'background', 'apns-priority': '5'}, payload=APNSPayload(aps=Aps(content_available=True))),
            token=device_token)
        return send(message)
    except UnregisteredError:
        MobileDevice.objects.filter(device_token=device_token).update(deactivated_at=now())

if __name__ == '__main__':
    import json
    import sys
    with open(sys.argv[1], 'r') as json_file:
        msg = json.load(json_file)
    print(send_to_device(device_token=sys.argv[2],msg=msg))
