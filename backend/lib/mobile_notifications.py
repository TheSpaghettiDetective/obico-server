import os
from firebase_admin.messaging import Message, send, Notification, AndroidConfig, APNSConfig, APNSPayload, Aps, UnregisteredError, SenderIdMismatchError
import firebase_admin
from django.utils.timezone import now
from sentry_sdk import capture_exception

from .utils import save_print_snapshot, shortform_duration, shortform_localtime, get_rotated_jpg_url
from app.models import calc_normalized_p, MobileDevice
from lib import cache

PRINT_EVENTS = ['PrintResumed', 'PrintPaused', 'PrintDone', 'PrintCancelled', 'PrintStarted', 'FilamentChange']
PRINT_PROGRESS_PUSH_INTERVAL = {'android': 60*5, 'ios': 60*20}

firebase_app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate(os.environ.get('FIREBASE_KEY'))) if os.environ.get('FIREBASE_KEY') else None


def send_if_needed(_print, op_event, op_data):
    if MobileDevice.objects.filter(user=_print.printer.user).count() < 1 or not _print.user.notification_enabled:
        return

    rotated_jpg_url = None      # Cache it as it's expensive to generate
    if op_event.get('event_type') in PRINT_EVENTS:
        rotated_jpg_url = get_rotated_jpg_url(_print.printer)
        send_print_event(_print, op_event.get('event_type'), rotated_jpg_url)

    send_print_progress(_print, op_data, rotated_jpg_url)


def send_failure_alert(printer, rotated_jpg_url, is_warning, print_paused):
    for mobile_device in MobileDevice.objects.filter(user=printer.user):
        data = dict(
            type='failureAlert',
            title=f'{"🟠 Print is fishy." if is_warning else "🔴 Failure is detected."} Printer {"" if print_paused else "not"} paused.',
            body=printer.current_print.filename,
            picUrl=rotated_jpg_url,
            printerId=str(printer.id),
        )

        send_to_device(data, mobile_device)


def send_print_event(_print, event_type, rotated_jpg_url):
    title = event_type.replace('Print', '')
    if event_type == 'FilamentChange':
        title = '🟠 Filament'

    for mobile_device in MobileDevice.objects.filter(user_id=_print.user_id):
        data = dict(
            type='printEvent',
            eventType=event_type,
            printId=str(_print.id),
            printerId=str(_print.printer.id),
            title=f"{title} | {_print.printer.name}",
            body=_print.filename,
            picUrl='',
        )
        if rotated_jpg_url:
            data['picUrl'] = rotated_jpg_url

        send_to_device(data, mobile_device)


def send_heater_event(printer, event, heater_name, actual_temperature):
    from lib.heater_trackers import HeaterEventType

    event_str = {
        HeaterEventType.TARGET_REACHED.value: 'Target reached',
        HeaterEventType.COOLED_DOWN.value: 'Cooled down'
    }[event]

    for mobile_device in MobileDevice.objects.filter(user=printer.user):
        data = dict(
            type='heaterEvent',
            eventType=event,
            printerId=str(printer.id),
            title=f'{heater_name} | {actual_temperature} ℃ | {event_str}',
            body=printer.name,
        )

        send_to_device(data, mobile_device)


def send_print_progress(_print, op_data, existed_rotated_jpg_url):
    rotated_jpg_url = existed_rotated_jpg_url       # Cache it as it's expensive to generate

    pushed_platforms = set()

    for mobile_device in MobileDevice.objects.filter(user=_print.user):
        if cache.print_status_mobile_push_get(_print.id, mobile_device.platform):
            continue
        pushed_platforms.add(mobile_device.platform)

        data = dict(
            type='printProgress',
            printId=str(_print.id),
            printerId=str(_print.printer.id),
            title='',
            body=_print.filename,
            picUrl='',
            completion='0'
        )

        state_text = op_data.get('state', {}).get('text', '')
        data['title'] += state_text if state_text.lower() != 'printing' else ''
        progress = op_data.get('progress')
        if progress:
            completion = progress.get('completion')
            data['completion'] = str(
                max(0, min(100, int(round(completion or 0)))))
            data['title'] += f' {data["completion"] if completion else "-"}%'
            seconds_left = progress.get("printTimeLeft") or 0
            if (
                isinstance(seconds_left, int) or
                isinstance(seconds_left, float)
            ):
                data['title'] += f' | ⏱{shortform_duration(seconds_left)}'
                if mobile_device.preferred_timezone:
                    data['title'] += f' | 🏁{shortform_localtime(seconds_left, mobile_device.preferred_timezone)}'

        printer = _print.printer
        if printer.not_watching_reason():
            data['title'] += ' | 💤'
        else:
            p = calc_normalized_p(printer.detective_sensitivity, printer.printerprediction)
            if p < 0.33:
                data['title'] += ' | 🟢'
            elif p < 0.66:
                data['title'] += ' | 🟠'
            else:
                data['title'] += ' | 🔴'

        if not rotated_jpg_url:
            rotated_jpg_url = get_rotated_jpg_url(_print.printer)
        if rotated_jpg_url:
            data['picUrl'] = rotated_jpg_url

        send_to_device(data, mobile_device)

    for pushed_platform in pushed_platforms:
        cache.print_status_mobile_push_set(_print.id, pushed_platform, PRINT_PROGRESS_PUSH_INTERVAL[pushed_platform])


def send_to_device(msg, mobile_device):
    if not firebase_app:
        return

    kwargs = dict(
        data=msg,
        android=AndroidConfig(priority='high'),
        apns=APNSConfig(
            headers={'apns-push-type': 'background', 'apns-priority': '5'},
            payload=APNSPayload(
                aps=Aps(content_available=True, category='post'))
        ),
        token=mobile_device.device_token
    )

    try:
        message = Message(**kwargs)
        return send(message, app=firebase_app)
    except (UnregisteredError, SenderIdMismatchError, firebase_admin.exceptions.InternalError):
        MobileDevice.objects.filter(device_token=mobile_device.device_token).update(deactivated_at=now())
    except Exception:
        import traceback; traceback.print_exc()
        capture_exception()


if __name__ == '__main__':
    import json
    import sys
    with open(sys.argv[1], 'r') as json_file:
        msg = json.load(json_file)
    print(send_to_device(device_token=sys.argv[2],msg=msg))
