from typing import Dict, Tuple

from app.models import User, NotificationSetting


def sync_plugin_of_user(
    user: User,
    name: str,
    enabled: bool,
    config: Dict,
    **kwargs
) -> Tuple['NotificationSetting', bool]:
    obj, created = NotificationSetting.objects.get_or_create(user=user, name=name)
    obj.enabled = enabled or kwargs.get('notify_on_failure_alert', False)
    obj.config = config
    obj.notify_on_failure_alert = kwargs.get('notify_on_failure_alert', True)
    obj.notify_on_print_done = kwargs.get('notify_on_print_done', user.notify_on_done if enabled else True)
    obj.notify_on_print_cancelled = kwargs.get('notify_on_print_cancelled', user.notify_on_canceled if enabled else False)
    obj.notify_on_filament_change = kwargs.get('notify_on_filament_change', user.notify_on_filament_change_req if enabled else False)
    obj.notify_on_other_events = kwargs.get('notify_on_other_events', False)
    obj.notify_on_heater_status = kwargs.get('notify_on_heater_status', False)
    obj.save()
    return obj, created


def sync_plugins_of_user(user: User) -> None:
    sync_plugin_of_user(
        user=user,
        name="discord",
        enabled=user.print_notification_by_discord,
        config={'webhook_url': user.discord_webhook or ''},
    )

    sync_plugin_of_user(
        user=user,
        name="pushover",
        enabled=user.print_notification_by_pushover,
        config={'user_key': user.pushover_user_token or ''}
    )

    sync_plugin_of_user(
        user=user,
        name="pushbullet",
        enabled=user.print_notification_by_pushover,
        config={'access_token': user.pushbullet_access_token or ''},
    )

    sync_plugin_of_user(
        user=user,
        name="telegram",
        enabled=user.print_notification_by_telegram,
        config={'chat_id': user.telegram_chat_id or ''},
    )

    sync_plugin_of_user(
        user=user,
        name="slack",
        enabled=True if user.slack_access_token else False,
        config={'access_token': user.slack_access_token or ''},
    )

    sync_plugin_of_user(
        user=user,
        name="email",
        enabled=True,
        config={},
        notify_on_failure_alert=user.alert_by_email,
    )

    sync_plugin_of_user(
        user=user,
        name="twillio",
        enabled=user.alert_by_sms,
        config={
            'phone_number': user.phone_number or '',
            'phone_country_code': user.phone_country_code or ''
        },
        notify_on_failure_alert=True,
        notify_on_print_done=False,
        notify_on_print_cancelled=False,
        notify_on_filament_change=False,
        notify_on_other_events=False,
        notify_on_heater_status=False,
    )
