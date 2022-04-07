from typing import Dict, Optional, Tuple, List
from types import ModuleType
import dataclasses
import os
import importlib
import importlib.util
import logging
from collections import OrderedDict
from raven.contrib.django.raven_compat.models import client as sentryClient  # type: ignore

from django.conf import settings

from .plugin import (
    BaseNotificationPlugin,
    PrinterNotificationContext, FailureNotificationContext,
    AccountNotificationContext,
    UserContext, PrintContext, PrinterContext,
    Feature,
)
from app.models import Print, Printer, NotificationSetting

from . import events


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
            sentryClient.captureException()


def _load_all_plugins() -> Dict[str, PluginDesc]:
    loaded: Dict[str, PluginDesc] = OrderedDict()
    for plugin_dir in settings.NOTIFICATION_PLUGIN_DIRS:
        _load_plugins(plugin_dir, loaded)
    return loaded


class Handler(object):

    def notification_plugin_names(self) -> List[str]:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        return list(_PLUGINS.keys())

    def notification_plugin_by_name(self, name) -> Optional[PluginDesc]:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        return _PLUGINS.get(name, None)

    def notification_plugins(self) -> List[PluginDesc]:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        return list(_PLUGINS.values())

    def send_failure_alerts(
        self,
        is_warning: bool,
        print_paused: bool,
        printer: Printer,
        print_: Print,
        poster_url: str,
        plugin_names: Tuple[str, ...] = (),
        fail_silently: bool = True,
    ) -> None:
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
            return

        user_ctx = UserContext.from_user(printer.user)
        printer_ctx = PrinterContext.from_printer(printer)
        print_ctx = PrintContext.from_print(print_, poster_url=poster_url)

        for nsetting in nsettings:
            try:
                assert nsetting.user_id == printer.user_id
                plugin = self.notification_plugin_by_name(nsetting.name)
                if not plugin:
                    continue

                context = FailureNotificationContext(
                    config=nsetting.config,
                    user=user_ctx,
                    printer=printer_ctx,
                    print=print_ctx,
                    site_is_public=settings.SITE_IS_PUBLIC,
                    is_warning=is_warning,
                    print_paused=print_paused,
                )

                extra_context = plugin.instance.build_failure_alert_extra_context(
                    user=printer.user,
                    print_=print_,
                    printer=printer,
                )

                self.send_failure_alert(nsetting=nsetting, context=context, **extra_context)
            except NotImplementedError:
                pass
            except Exception:
                if fail_silently:
                    LOGGER.exception('send_failure_alert plugin error')
                    sentryClient.captureException()
                else:
                    raise

    def feature_for_event(self, event_name: str, event_data: Dict) -> Optional[Feature]:
        if event_name in (events.PrintFailed, events.PrintDone):
            return Feature.notify_on_print_done

        if event_name == events.PrintCancelled:
            return Feature.notify_on_print_cancelled

        if event_name == events.FilamentChange:
            return Feature.notify_on_filament_change

        if event_name in (events.HeaterCooledDown, events.HeaterTargetReached):
            return Feature.notify_on_heater_status

        if event_name == events.PrintProgress:
            # return Feature.notify_on_print_progress # TODO
            return None

        if event_name in events.OTHER_PRINT_EVENTS:
            return Feature.notify_on_other_events

        return None

    def should_plugin_handle_printer_event(
        self,
        plugin: BaseNotificationPlugin,
        nsetting: NotificationSetting,
        event_name: str,
        event_data: Dict,
    ) -> bool:
        feature = self.feature_for_event(event_name, event_data)

        # is event is expected at all?
        if not feature:
            return False

        supported = plugin.supported_features()

        # does plugin support feature/event?
        if feature not in supported:
            return False

        # is feature enabled in user's configuration?
        return getattr(nsetting, feature.name, False) and nsetting.enabled

    def send_printer_notifications(
        self,
        event_name: str,
        event_data: dict,
        printer: Printer,
        print_: Optional[Print],
        poster_url: str,
        plugin_names: Tuple[str, ...] = (),
        fail_silently: bool = True,
    ) -> None:
        feature = self.feature_for_event(event_name, event_data)
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
            return

        user_ctx = UserContext.from_user(printer.user)
        printer_ctx = PrinterContext.from_printer(printer)
        print_ctx = PrintContext.from_print(print_, poster_url=poster_url)

        for nsetting in nsettings:
            try:
                assert nsetting.user_id == printer.user_id
                plugin = self.notification_plugin_by_name(nsetting.name)
                if not plugin:
                    continue

                context = PrinterNotificationContext(
                    config=nsetting.config,
                    user=user_ctx,
                    printer=printer_ctx,
                    print=print_ctx,
                    site_is_public=settings.SITE_IS_PUBLIC,
                    event_name=event_name,
                    event_data=event_data,
                )

                extra_context = plugin.instance.build_print_notifications_extra_context(
                    user=printer.user,
                    print_=print_,
                    printer=printer,
                )

                self.send_printer_notification(nsetting=nsetting, context=context, **extra_context)
            except NotImplementedError:
                pass
            except Exception:
                if fail_silently:
                    LOGGER.exception('send_printer_notification plugin error')
                    sentryClient.captureException()
                else:
                    raise

    def send_failure_alert(
        self,
        nsetting: NotificationSetting,
        context: FailureNotificationContext,
        **extra_context,
    ) -> None:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        if not nsetting.notify_on_failure_alert:
            return

        plugin = _PLUGINS[nsetting.name]
        plugin.instance.send_failure_alert(context=context, **extra_context)

    def send_printer_notification(
        self,
        nsetting: NotificationSetting,
        context: PrinterNotificationContext,
        **extra_context,
    ) -> None:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        plugin = _PLUGINS[nsetting.name]

        if not self.should_plugin_handle_printer_event(
            plugin.instance,
            nsetting,
            context.event_name,
            context.event_data,
        ):
            return

        plugin.instance.send_printer_notification(context=context, **extra_context)

    def send_account_notification(
        self,
        nsetting: NotificationSetting,
        context: AccountNotificationContext,
    ) -> None:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        plugin = _PLUGINS[nsetting.name]
        plugin.instance.send_account_notification(context=context)

    def send_test_notification(self, nsetting: NotificationSetting) -> None:
        global _PLUGINS
        if _PLUGINS is None:
            _PLUGINS = _load_all_plugins()

        plugin = _PLUGINS[nsetting.name]
        plugin.instance.send_test_notification(config=nsetting.config)

    def queue_send_printer_notifications_task(
        self,
        event_name: str,
        event_data: dict,
        printer: Printer,
        print_: Optional[Print],
        poster_url: str = '',
    ) -> None:
        feature = self.feature_for_event(event_name, event_data)
        if not feature:
            return

        should_fire = NotificationSetting.objects.filter(
            user_id=printer.user_id,
            enabled=True,
            name__in=self.notification_plugin_names(),
            **{feature.name: True},
        ).exists()

        if should_fire:
            from . import tasks
            tasks.send_printer_notifications.apply_async(
                kwargs={
                    'printer_id': printer.id,
                    'event_name': event_name,
                    'event_data': event_data,
                    'print_id': print_.id if print_ else None,
                    'poster_url': poster_url,
                }
            )
