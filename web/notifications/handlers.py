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


__PLUGINS: Optional[Dict[str, PluginDesc]] = None


def _load_plugin(name: str, path: str) -> PluginDesc:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    instance = module.__load_plugin__()
    return PluginDesc(name=name, path=path, module=module, instance=instance)


def _load_plugins(root: Optional[str] = None) -> Dict[str, PluginDesc]:
    root = root if root else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
    loaded = OrderedDict()
    candidates = [
        name for name in os.listdir(root)
        if (
            os.path.isdir(os.path.join(root, name)) and
            os.path.exists(os.path.join(os.path.join(root, name), '__init__.py')) and
            name[0] not in ('.', '_')
        )
    ]
    for name in candidates:
        path = os.path.join(os.path.join(root, name), '__init__.py')
        try:
            loaded[name] = _load_plugin(name, path)
        except Exception:
            logging.exception('ops')
            sentryClient.captureException()

    return loaded


def notification_plugin_names() -> List[str]:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    return list(__PLUGINS.keys())


def notification_plugins_by_name(name) -> Optional[PluginDesc]:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    return __PLUGINS.get(name, None)


def notification_plugins() -> List[PluginDesc]:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    return list(__PLUGINS.values())


def send_failure_alerts(
    is_warning: bool,
    print_paused: bool,
    printer: Printer,
    print_: Print,
    poster_url: str,
    plugin_names: Tuple[str, ...] = (),
    fail_silently: bool = True,
) -> None:
    if plugin_names:
        names = list(set(notification_plugin_names()) & set(plugin_names))
    else:
        names = notification_plugin_names()

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
            context = FailureNotificationContext(
                config=nsetting.config,
                user=user_ctx,
                printer=printer_ctx,
                print=print_ctx,
                site_is_public=settings.SITE_IS_PUBLIC,
                is_warning=is_warning,
                print_paused=print_paused,
            )

            send_failure_alert(nsetting=nsetting, context=context)
        except NotImplementedError:
            pass
        except Exception:
            if fail_silently:
                LOGGER.exception('send_failure_alert plugin error')
                sentryClient.captureException()
            else:
                raise


def feature_for_event(event_name: str, event_data: Dict) -> Optional[Feature]:
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

    if events.is_supported(event_name):
        return Feature.notify_on_other_events

    return None


def should_plugin_handle_printer_event(
    plugin: BaseNotificationPlugin,
    nsetting: NotificationSetting,
    event_name: str,
    event_data: Dict,
) -> bool:
    feature = feature_for_event(event_name, event_data)

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
    event_name: str,
    event_data: dict,
    printer: Printer,
    print_: Optional[Print],
    poster_url: str,
    plugin_names: Tuple[str, ...] = (),
    fail_silently: bool = True,
) -> None:
    feature = feature_for_event(event_name, event_data)
    if not feature:
        return

    if plugin_names:
        names = list(set(notification_plugin_names()) & set(plugin_names))
    else:
        names = notification_plugin_names()

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
            context = PrinterNotificationContext(
                config=nsetting.config,
                user=user_ctx,
                printer=printer_ctx,
                print=print_ctx,
                site_is_public=settings.SITE_IS_PUBLIC,
                event_name=event_name,
                event_data=event_data,
            )

            send_printer_notification(nsetting, context)
        except NotImplementedError:
            pass
        except Exception:
            if fail_silently:
                LOGGER.exception('send_printer_notification plugin error')
                sentryClient.captureException()
            else:
                raise


def send_failure_alert(
    nsetting: NotificationSetting,
    context: FailureNotificationContext,
) -> None:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    if not nsetting.notify_on_failure_alert:
        return

    plugin = __PLUGINS[nsetting.name]
    plugin.instance.send_failure_alert(context=context)


def send_printer_notification(
    nsetting: NotificationSetting,
    context: PrinterNotificationContext,
) -> None:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    plugin = __PLUGINS[nsetting.name]

    if not should_plugin_handle_printer_event(
        plugin.instance,
        nsetting,
        context.event_name,
        context.event_data
    ):
        return

    plugin.instance.send_printer_notification(context=context)


def send_test_notification(nsetting: NotificationSetting) -> None:
    global __PLUGINS
    if __PLUGINS is None:
        __PLUGINS = _load_plugins()

    plugin = __PLUGINS[nsetting.name]
    plugin.instance.send_test_notification(config=nsetting.config)
