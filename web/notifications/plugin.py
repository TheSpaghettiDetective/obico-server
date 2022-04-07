from typing import Dict, Optional, Generator, Set
import datetime
import dataclasses
import requests  # type: ignore
import enum
from rest_framework.serializers import ValidationError as ValidationError  # noqa: F401
from raven.contrib.django.raven_compat.models import client as sentryClient  # type: ignore

from app.models import Print, Printer, User
from lib import site as site  # noqa: F401
from . import events


@dataclasses.dataclass(frozen=True)
class PrinterContext:
    id: int
    name: str
    pause_on_failure: bool
    watching_enabled: bool

    @classmethod
    def from_printer(cls, printer: Printer) -> 'PrinterContext':
        return PrinterContext(
            id=printer.id,
            name=printer.name,
            pause_on_failure=printer.action_on_failure == printer.PAUSE,
            watching_enabled=printer.watching_enabled,
        )


def get_poster_url_content(poster_url: str, timeout: Optional[float] = 5.0) -> Generator[Optional[bytes], Optional[float], None]:
    # generator, receives timeout and then retreives file content from cache or network
    content: Optional[bytes] = None
    while True:
        timeout = (yield content) or timeout

        if not poster_url:
            continue

        if content is not None:
            continue

        try:
            resp = requests.get(poster_url, timeout=timeout)
            resp.raise_for_status()
        except Exception:
            sentryClient.captureException()
            continue

        content = resp.content


@dataclasses.dataclass(frozen=True)
class PrintContext:
    id: int
    filename: str

    poster_url: str
    _poster_url_fetcher: Generator[Optional[bytes], Optional[float], None]

    started_at: Optional[datetime.datetime]
    ended_at: Optional[datetime.datetime]
    alerted_at: Optional[datetime.datetime]

    alert_overwrite: str

    @classmethod
    def from_print(cls, _print: Optional[Print], poster_url: str, timeout: float = 5.0) -> 'PrintContext':
        alert_overwrite: str = _print.alert_overwrite or ''  # type: ignore
        ctx = PrintContext(
            id=_print.id if _print else 0,
            filename=_print.filename if _print else '',
            poster_url=poster_url or '',
            _poster_url_fetcher=get_poster_url_content(poster_url or '', timeout=timeout),
            started_at=_print.started_at if _print else None,
            alerted_at=_print.alerted_at if _print else None,
            ended_at=(_print.finished_at or _print.cancelled_at or None) if _print else None,
            alert_overwrite=alert_overwrite,
        )

        ctx._poster_url_fetcher.send(None)
        return ctx

    def get_poster_url_content(self, timeout: float = 5.0) -> Optional[bytes]:
        # We need to avoid refetching same image many times.
        # This class is frozen as it reused accross notification handler calls, what should not tamper it.
        # Adding this "generator-style caching" to the class.
        return self._poster_url_fetcher.send(timeout)


@dataclasses.dataclass(frozen=True)
class UserContext:
    id: int
    email: str
    first_name: str
    last_name: str

    dh_balance: float
    is_pro: bool

    @classmethod
    def from_user(cls, user: User) -> 'UserContext':
        return UserContext(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            dh_balance=user.dh_balance,
            is_pro=user.is_pro,
        )


@dataclasses.dataclass(frozen=True)
class NotificationContext:
    config: Dict
    user: UserContext
    printer: PrinterContext
    print: PrintContext
    site_is_public: bool


@dataclasses.dataclass(frozen=True)
class FailureAlertContext(NotificationContext):
    is_warning: bool
    print_paused: bool


@dataclasses.dataclass(frozen=True)
class PrinterNotificationContext(NotificationContext):
    event_name: str
    event_data: Dict


class Feature(enum.Enum):
    notify_on_failure_alert = 'notify_on_failure_alert'
    notify_on_account_events = 'notify_on_account_events'
    notify_on_print_done = 'notify_on_print_done'
    notify_on_print_cancelled = 'notify_on_print_cancelled'
    notify_on_filament_change = 'notify_on_filament_change'
    notify_on_other_events = 'notify_on_other_events'
    notify_on_heater_status = 'notify_on_heater_status'
    notify_on_print_progress = 'notify_on_print_progress'


class BaseNotificationPlugin(object):

    def validate_config(self, data: Dict) -> Dict:
        return data

    def send_failure_alert(self, context: FailureAlertContext, **kwargs) -> None:
        raise NotImplementedError

    def send_printer_notification(self, context: PrinterNotificationContext, **kwargs) -> None:
        raise NotImplementedError

    def send_test_notification(self, config: Dict, **kwargs) -> None:
        raise NotImplementedError

    def build_failure_alert_extra_context(self, **kwargs) -> Dict:
        return {}

    def build_print_notification_extra_context(self, **kwargs) -> Dict:
        return {}

    def supported_features(self) -> Set[Feature]:
        return {
            Feature.notify_on_failure_alert,
            Feature.notify_on_print_done,
            Feature.notify_on_print_cancelled,
            Feature.notify_on_filament_change,
            Feature.notify_on_other_events,
        }

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
        return 'The Spaghetti Detective - Failure alert!'

    def get_failure_alert_text(self, context: FailureAlertContext, link: Optional[str] = None, **kwargs) -> str:
        pausing_msg = ''
        if context.print_paused:
            pausing_msg = 'Printer is paused.'
        elif context.printer.pause_on_failure and context.is_warning:
            pausing_msg = 'Printer is NOT paused because The Detective is not very sure about it.'

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
        return 'The Spaghetti Detective - Print job notification'

    def get_printer_notification_text(self, context: PrinterNotificationContext) -> str:
        text = f"Your print job {self.b(context.print.filename)} "
        event_name = context.event_name
        event_data = context.event_data

        if event_name == events.PrintStarted:
            text += "has started "
        elif event_name == events.PrintFailed:
            text += "failed "
        elif event_name == events.PrintDone:
            text += "is ready "
        elif event_name == events.PrintCancelled:
            text += "is canceled "
        elif event_name == events.PrintPaused:
            text += "is paused "
        elif event_name == events.PrintResumed:
            text += "is resumed "
        elif event_name == events.FilamentChange:
            text += "requires filament change "
        elif event_name == events.HeaterCooledDown:
            text = (
                f"Heater {self.b(event_data['name'])} "
                f"has cooled down to {self.b(str(event_data['actual']) + '℃')}"
            )
        elif event_name == events.HeaterTargetReached:
            text = (
                f"Heater {self.b(event_data['name'])} "
                f"has reached target temperature {self.b(str(event_data['actual']) + '℃')} "
            )
        else:
            return ''

        text += f"on printer {self.i(context.printer.name)}."
        return text
