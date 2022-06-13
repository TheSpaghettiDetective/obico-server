from typing import Dict, Optional, Tuple, List, Generator
from types import ModuleType
import dataclasses
import os
import importlib
import importlib.util
import logging
import requests  # type: ignore
from collections import OrderedDict
from sentry_sdk import capture_exception

from django.conf import settings

from .plugin import (
    BaseNotificationPlugin,
    PrinterNotificationContext, FailureAlertContext,
    UserContext, PrintContext, PrinterContext, TestMessageContext,
    Feature,
)
from app.models import Print, Printer, NotificationSetting, User
from lib import mobile_notifications
from lib.utils import get_rotated_jpg_url

from . import notification_types


LOGGER = logging.getLogger(__file__)


@dataclasses.dataclass
class PluginDesc:
    name: str
    path: str
    module: ModuleType
    instance: BaseNotificationPlugin


_PLUGINS: Optional[Dict[str, PluginDesc]] = None


def _load_plugin(name: str, path: str) -> PluginDesc:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    instance = module.__load_plugin__()
    return PluginDesc(name=name, path=path, module=module, instance=instance)


def _load_plugins(root: str, loaded: Dict[str, PluginDesc]) -> None:
    candidates = [
        name for name in os.listdir(root)
        if (
            os.path.isdir(os.path.join(root, name)) and
            os.path.exists(os.path.join(os.path.join(root, name), '__init__.py')) and
            name[0] not in ('.', '_')
        )
    ]

    for name in candidates:
        if name in loaded:
            LOGGER.warning(f'skipped loading plugin "{name}", already loaded from {loaded["name"].path}')
            continue

        path = os.path.join(os.path.join(root, name), '__init__.py')
        try:
            loaded[name] = _load_plugin(name, path)
        except Exception:
            logging.exception(f'error loading plugin "{name}" from {path}')
            capture_exception()


def _load_all_plugins() -> Dict[str, PluginDesc]:
    loaded: Dict[str, PluginDesc] = OrderedDict()
    for plugin_dir in settings.NOTIFICATION_PLUGIN_DIRS:
        _load_plugins(plugin_dir, loaded)
    return loaded


class Handler(object):

    def __init__(self) -> None:
        self._PLUGINS: Optional[Dict[str, PluginDesc]] = None

    def notification_plugin_names(self) -> List[str]:
        if self._PLUGINS is None:
            self._PLUGINS = _load_all_plugins()
        return list(self._PLUGINS.keys())

    def notification_plugin_by_name(self, name) -> Optional[PluginDesc]:
        if self._PLUGINS is None:
            self._PLUGINS = _load_all_plugins()
        return self._PLUGINS.get(name, None)

    def notification_plugins(self) -> List[PluginDesc]:
        if self._PLUGINS is None:
            self._PLUGINS = _load_all_plugins()
        return list(self._PLUGINS.values())

    def get_printer_context(self, printer: Printer) -> PrinterContext:
        return PrinterContext(
            id=printer.id,
            name=printer.name,
            pause_on_failure=printer.action_on_failure == printer.PAUSE,
            watching_enabled=printer.watching_enabled,
        )

    def get_print_context(self, _print: Optional[Print]) -> PrintContext:
        alert_overwrite: str = (_print.alert_overwrite or '') if _print is not None else ''
        ctx = PrintContext(
            id=_print.id if _print else 0,
            filename=_print.filename if _print else '',
            started_at=_print.started_at if _print else None,
            alerted_at=_print.alerted_at if _print else None,
            ended_at=(_print.finished_at or _print.cancelled_at or None) if _print else None,
            alert_overwrite=alert_overwrite,
        )

        return ctx

    def get_user_context(self, user: User) -> UserContext:
        return UserContext(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            dh_balance=user.dh_balance,
            is_pro=user.is_pro,
            unsub_token=user.unsub_token,
        )

    def send_failure_alerts(
        self,
        is_warning: bool,
        print_paused: bool,
        printer: Printer,
        print_: Print,
        img_url: str,
        extra_context: Optional[Dict] = None,
        plugin_names: Tuple[str, ...] = (),
        fail_silently: bool = True,
    ) -> None:
        try:
            mobile_notifications.send_failure_alert(printer, img_url, is_warning, print_paused)
        except Exception:
            capture_exception()

        if plugin_names:
            names = list(set(self.notification_plugin_names()) & set(plugin_names))
        else:
            names = self.notification_plugin_names()

        # select matching, enabled & configured
        nsettings = list(NotificationSetting.objects.filter(
            user_id=printer.user_id,
            enabled=True,
            name__in=names,
            notify_on_failure_alert=True
        ))

        if not nsettings:
            LOGGER.debug("no matching NotificationSetting objects, ignoring failure alert")
            return

        user_ctx = self.get_user_context(printer.user)
        printer_ctx = self.get_printer_context(printer)
        print_ctx = self.get_print_context(print_)
        
        for nsetting in nsettings:
            LOGGER.debug(f'forwarding failure alert to plugin "{nsetting.name}" (pk: {nsetting.pk})')
            try:
                plugin = self.notification_plugin_by_name(nsetting.name)
                if not plugin:
                    continue

                context = FailureAlertContext(
                    config=nsetting.config,
                    user=user_ctx,
                    printer=printer_ctx,
                    print=print_ctx,
                    is_warning=is_warning,
                    print_paused=print_paused,
                    extra_context=extra_context,
                    img_url=img_url,
                )

                self._send_failure_alert(nsetting=nsetting, context=context)
            except NotImplementedError:
                pass
            except Exception:
                if fail_silently:
                    LOGGER.exception('send_failure_alert plugin error')
                    capture_exception()
                else:
                    raise

    def feature_for_notification_type(self, notification_type: str, notification_data: Dict) -> Optional[Feature]:
        if notification_type == notification_types.PrintDone:
            return Feature.notify_on_print_done

        if notification_type == notification_types.PrintCancelled:
            return Feature.notify_on_print_cancelled

        if notification_type == notification_types.FilamentChange:
            return Feature.notify_on_filament_change

        if notification_type in (notification_types.HeaterCooledDown, notification_types.HeaterTargetReached):
            return Feature.notify_on_heater_status

        if notification_type in list(notification_types.OTHER_PRINT_EVENT_MAP.values()):
            return Feature.notify_on_other_print_events

        return None

    def should_plugin_handle_notification_type(
        self,
        plugin: BaseNotificationPlugin,
        nsetting: NotificationSetting,
        notification_type: str,
        notification_data: Dict,
    ) -> bool:
        if not nsetting.enabled:
            LOGGER.debug(f'notifications are disabled for plugin "{nsetting.name}" (pk: {nsetting.pk}), ignoring event')
            return False

        feature = self.feature_for_notification_type(notification_type, notification_data)

        # is event is expected at all?
        if not feature:
            LOGGER.debug(f'{notification_type} is not expected, ignoring event')
            return False

        supported = plugin.supported_features()

        # does plugin support feature/event?
        if feature not in supported:
            LOGGER.debug(f'{feature.name} is not supported by plugin "{nsetting.name}", ignoring event')
            return False

        # is feature enabled in user's configuration?
        if getattr(nsetting, feature.name, False):
            return True

        LOGGER.debug(f'{feature.name} is not enabled for plugin "{nsetting.name}" (pk: {nsetting.pk}), ignoring event')
        return False

    def send_printer_notifications(
        self,
        notification_type: str,
        notification_data: dict,
        printer: Printer,
        print_: Optional[Print],
        extra_context: Optional[Dict] = None,
        plugin_names: Tuple[str, ...] = (),
        fail_silently: bool = True,
    ) -> None:
        feature = self.feature_for_notification_type(notification_type, notification_data)
        if not feature:
            return

        if plugin_names:
            names = list(set(self.notification_plugin_names()) & set(plugin_names))
        else:
            names = self.notification_plugin_names()

        # select matching, enabled & configured
        nsettings = list(NotificationSetting.objects.filter(
            user_id=printer.user_id,
            enabled=True,
            name__in=names,
            **{feature.name: True}
        ))

        if not nsettings:
            LOGGER.debug("no matching NotificationSetting objects, ignoring printer notification")
            return

        if print_ and print_.poster_url:
            img_url = print_.poster_url
        else:
            img_url = get_rotated_jpg_url(printer, force_snapshot=True)

        user_ctx = self.get_user_context(printer.user)
        printer_ctx = self.get_printer_context(printer)
        print_ctx = self.get_print_context(print_)
        
        for nsetting in nsettings:
            LOGGER.debug(f'forwarding event {"notification_type"} to plugin "{nsetting.name}" (pk: {nsetting.pk})')
            try:
                plugin = self.notification_plugin_by_name(nsetting.name)
                if not plugin:
                    continue

                context = PrinterNotificationContext(
                    feature=feature,
                    config=nsetting.config,
                    user=user_ctx,
                    printer=printer_ctx,
                    print=print_ctx,
                    notification_type=notification_type,
                    notification_data=notification_data,
                    extra_context=extra_context or {},
                    img_url=img_url,
                )

                self._send_printer_notification(nsetting=nsetting, context=context)
            except NotImplementedError:
                pass
            except Exception:
                if fail_silently:
                    LOGGER.exception('send_printer_notification plugin error')
                    capture_exception()
                else:
                    raise

    def _send_failure_alert(
        self,
        nsetting: NotificationSetting,
        context: FailureAlertContext,
    ) -> None:
        if not nsetting.notify_on_failure_alert:
            return

        plugin = self.notification_plugin_by_name(nsetting.name)
        if not plugin:
            return

        plugin.instance.send_failure_alert(context=context)

    def _send_printer_notification(
        self,
        nsetting: NotificationSetting,
        context: PrinterNotificationContext,
    ) -> None:
        plugin = self.notification_plugin_by_name(nsetting.name)
        if not plugin:
            return

        if not self.should_plugin_handle_notification_type(
            plugin.instance,
            nsetting,
            context.notification_type,
            context.notification_data,
        ):
            return

        plugin.instance.send_printer_notification(context=context)

    def send_test_message(self, nsetting: NotificationSetting, extra_context: Optional[Dict] = None) -> None:
        plugin = self.notification_plugin_by_name(nsetting.name)

        context = TestMessageContext(
            config=nsetting.config,
            user=self.get_user_context(nsetting.user),
            extra_context=extra_context or {},
        )

        plugin.instance.send_test_message(context=context)

    def queue_send_printer_notifications_task(
        self,
        notification_type: str,
        notification_data: dict,
        printer: Printer,
        print_: Optional[Print],
        extra_context: Optional[Dict] = None,
        in_process: Optional[bool] = False,
    ) -> None:
        feature = self.feature_for_notification_type(notification_type, notification_data)
        if not feature or not printer.user.notification_enabled:
            return

        should_fire = NotificationSetting.objects.filter(
            user_id=printer.user_id,
            enabled=True,
            name__in=self.notification_plugin_names(),
            **{feature.name: True},
        ).exists()

        if not should_fire:
            LOGGER.debug('no matching NotificationSetting objects, ignoring event')

        kwargs = {
                'printer_id': printer.id,
                'notification_type': notification_type,
                'notification_data': notification_data,
                'print_id': print_.id if print_ else None,
                'extra_context': extra_context,

            }
        from . import tasks
        if in_process:
            tasks.send_printer_notifications(**kwargs)
        else:
            tasks.send_printer_notifications.apply_async(kwargs=kwargs)
