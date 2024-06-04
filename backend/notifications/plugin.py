from typing import Dict, Optional, Generator, Set
import datetime
import dataclasses
import enum

from . import notification_types


@dataclasses.dataclass(frozen=True)
class PrinterContext:
    id: int
    name: str
    pause_on_failure: bool
    watching_enabled: bool


@dataclasses.dataclass(frozen=True)
class PrintContext:
    id: int
    filename: str

    started_at: Optional[datetime.datetime]
    ended_at: Optional[datetime.datetime]
    alerted_at: Optional[datetime.datetime]

    alert_overwrite: str


class Feature(enum.Enum):
    notify_on_failure_alert = 'notify_on_failure_alert'
    notify_on_print_done = 'notify_on_print_done'
    notify_on_print_cancelled = 'notify_on_print_cancelled'
    notify_on_filament_change = 'notify_on_filament_change'
    notify_on_heater_status = 'notify_on_heater_status'
    notify_on_print_start = 'notify_on_print_start',
    notify_on_print_pause =  'notify_on_print_pause',
    notify_on_print_resume = 'notify_on_print_resume',


@dataclasses.dataclass(frozen=True)
class UserContext:
    id: int
    email: str
    syndicate_name: str
    first_name: str
    last_name: str
    unsub_token: str
    dh_balance: float
    is_pro: bool


@dataclasses.dataclass(frozen=True)
class NotificationContext:
    config: Dict
    user: UserContext
    printer: PrinterContext
    print: PrintContext
    extra_context: Dict
    img_url: str


@dataclasses.dataclass(frozen=True)
class FailureAlertContext(NotificationContext):
    is_warning: bool
    print_paused: bool


@dataclasses.dataclass(frozen=True)
class PrinterNotificationContext(NotificationContext):
    feature: Feature
    notification_type: str


@dataclasses.dataclass(frozen=True)
class TestMessageContext:
    config: Dict
    user: UserContext
    extra_context: Dict


class BaseNotificationPlugin(object):

    ## Public APIs.

    def validate_config(self, data: Dict) -> Dict:
        return data

    def send_failure_alert(self, context: FailureAlertContext) -> None:
        raise NotImplementedError

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:
        raise NotImplementedError

    def send_test_message(self, context: TestMessageContext) -> None:
        raise NotImplementedError

    def supported_features(self) -> Set[Feature]:
        return {
            Feature.notify_on_failure_alert,
            Feature.notify_on_print_done,
            Feature.notify_on_print_cancelled,
            Feature.notify_on_filament_change,
            Feature.notify_on_heater_status,
            Feature.notify_on_print_start,
            Feature.notify_on_print_pause,
            Feature.notify_on_print_resume,
        }

    def env_vars(self) -> Dict:
        return {}


    ## APIs reserved for Obico internal use. Do not override.

    def i(self, s: str) -> str:
        # format to italic
        return s

    def b(self, s: str) -> str:
        # format to bold
        return s

    def u(self, s: str) -> str:
        # format underscore
        return s

    def get_failure_alert_title(
        self,
        context: FailureAlertContext,
        link: Optional[str] = None,
        **kwargs
    ) -> str:
        return 'Obico - Failure alert!'

    def get_failure_alert_text(self, context: FailureAlertContext, link: Optional[str] = None, **kwargs) -> str:
        pausing_msg = ''
        if context.print_paused:
            pausing_msg = 'Printer is paused.'
        elif context.printer.pause_on_failure and context.is_warning:
            pausing_msg = 'Printer is NOT paused.'

        text = 'Your print {} on {} {}.\n{}'.format(
            self.b(context.print.filename),
            self.i(context.printer.name),
            'smells fishy' if context.is_warning else 'is probably failing',
            pausing_msg,
        )
        if link:
            text += f"\nGo check it at: {link}"

        return text

    def get_printer_notification_title(self, context: PrinterNotificationContext) -> str:
        return 'Obico - Print job notification'

    def get_printer_notification_text(self, context: PrinterNotificationContext) -> str:
        text = f"Your print job {self.b(context.print.filename)} "
        notification_type = context.notification_type
        extra_context = context.extra_context

        if notification_type == notification_types.PrintStarted:
            text += "has started "
        elif notification_type == notification_types.PrintDone:
            text += "is ready "
        elif notification_type == notification_types.PrintCancelled:
            text += "is canceled "
        elif notification_type == notification_types.PrintPaused:
            text += "is paused "
        elif notification_type == notification_types.PrintResumed:
            text += "is resumed "
        elif notification_type == notification_types.FilamentChange:
            text += "requires filament change "
        elif notification_type == notification_types.HeaterCooledDown:
            text = (
                f"Heater {self.b(extra_context['heater_name'])} "
                f"has cooled down to {self.b(str(extra_context['heater_actual']) + '℃')} "
            )
        elif notification_type == notification_types.HeaterTargetReached:
            text = (
                f"Heater {self.b(extra_context['heater_name'])} "
                f"has reached target temperature {self.b(str(extra_context['heater_actual']) + '℃')} "
            )
        else:
            return ''

        text += f"on printer {self.i(context.printer.name)}."
        return text
