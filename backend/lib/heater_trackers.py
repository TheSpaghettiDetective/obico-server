import enum
import dataclasses
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple, Set
import logging

from app.models import Printer, HeaterTracker, PrintHeaterTarget
from lib.mobile_notifications import send_heater_event as send_mobile_push_heater_event
from notifications.notification_types import HeaterCooledDown, HeaterTargetReached
from notifications.handlers import handler
from django.utils.timezone import now
from django.db import IntegrityError


COOLDOWN_THRESHOLD = 35.0  # degree celsius
TARGET_REACHED_DELTA = 0.25  # degree celsius

LOGGER = logging.getLogger(__file__)


def float_or_none(v):
    if v is None or v == '':
        return None
    return float(v)


class UpdateError(Exception):
    pass


class HeaterEventType(enum.Enum):
    TARGET_REACHED = 'ReachedTarget'
    COOLED_DOWN = 'CooledDown'


@dataclasses.dataclass
class HeaterState:
    name: str
    actual: Optional[float]
    target: Optional[float]
    offset: float

    def has_been_cooled_down(self) -> bool:
        return (
            self.target is not None and
            self.actual is not None and
            self.target <= COOLDOWN_THRESHOLD and
            self.actual <= COOLDOWN_THRESHOLD
        )

    def has_reached_target(self) -> bool:
        return (
            self.target is not None and
            self.actual is not None and
            self.target > COOLDOWN_THRESHOLD and
            abs(self.target - self.actual) < TARGET_REACHED_DELTA
        )

    def event_type_if_any(self) -> Optional[HeaterEventType]:
        if self.has_been_cooled_down():
            return HeaterEventType.COOLED_DOWN
        if self.has_reached_target():
            return HeaterEventType.TARGET_REACHED
        return None


@dataclasses.dataclass
class HeaterEvent:
    type: HeaterEventType
    state: HeaterState

    def type_as_str(self):
        return self.type.value


def parse_states(d: Dict[str, Dict[str, Any]]) -> Dict[str, HeaterState]:
    """
    {'tool0': {'actual': 90.0, 'target': 90.0, 'offset': 0},
     'bed': {'actual': 40.0, 'target': 40.0, 'offset': 0},
     'chamber': {'actual': None, 'target': None, 'offset': 0}}
    """
    return {
        name: HeaterState(name=name, target=float_or_none(v['target']),
                          actual=float_or_none(v['actual']),
                          offset=float_or_none(v.get('offset', 0)))
        for name, v in d.items()
    }


def calc_changes(trackers: List[HeaterTracker],
                 heaters: List[HeaterState]) -> List[Tuple[HeaterTracker, bool, Optional[HeaterEvent]]]:
    trackersd = {t.name: t for t in trackers}
    seen: Set[str] = set()

    ret = []
    for heater in heaters:
        if heater.name in seen:
            continue

        seen.add(heater.name)

        if heater.target is None:
            # existing tracker (if any) is going to be purged
            # without notification
            continue

        dirty: bool = False
        event: Optional[HeaterEvent] = None

        tracker = trackersd.pop(heater.name, None)
        if tracker is not None:
            if tracker.target == heater.target:
                # tracked heater with unchanged target,
                # notification is necessary only when
                # target is reached
                if not tracker.reached:
                    etype = heater.event_type_if_any()
                    if etype is not None:
                        dirty = True
                        tracker.reached = True
                        event = HeaterEvent(type=etype, state=heater)
            else:
                # tracked heater has new target,
                # notify if target's been reached already
                dirty = True
                tracker.target = heater.target
                tracker.reached = False
                etype = heater.event_type_if_any()
                if etype is not None:
                    tracker.reached = True
                    event = HeaterEvent(type=etype, state=heater)

        else:
            # not yet tracked heater,
            # notify if target's been reached already
            dirty = True
            tracker = HeaterTracker(
                name=heater.name,
                target=heater.target,
                reached=False,
            )
            etype = heater.event_type_if_any()
            if etype is not None:
                tracker.reached = True
                event = HeaterEvent(type=etype, state=heater)

        ret.append((tracker, dirty, event))

    return ret


def update_heater_trackers(printer: Printer,
                           trackers: List[HeaterTracker],
                           temp_data: Dict,
                           now_: Optional[datetime] = None) -> List[HeaterTracker]:
    new_updated_at = now_ or now()
    heaters = list(parse_states(temp_data).values())

    trackersd = {tracker.name: tracker for tracker in trackers}
    changes = calc_changes(trackers, heaters)

    new_trackers = []
    for tracker, dirty, event in changes:
        new_trackers.append(tracker)

        trackersd.pop(tracker.name, None)

        if dirty:
            if tracker.id:
                touched = HeaterTracker.objects.filter(
                    name=tracker.name,
                    printer=printer,
                    updated_at=tracker.updated_at
                ).update(
                    name=tracker.name,
                    target=tracker.target,
                    reached=tracker.reached,
                    updated_at=new_updated_at
                )
                if not touched:
                    raise UpdateError()
            else:
                tracker.printer = printer
                tracker.save()

        if event is not None:
            send_mobile_push_heater_event(
                printer,
                event=event.type_as_str(),
                heater_name=event.state.name,
                # 0.0 for pleasing mypy, actual cannot be None here
                actual_temperature=event.state.actual or 0.0)

            handler.queue_send_printer_notifications_task(
                printer=printer,
                notification_type=HeaterTargetReached if event.type == HeaterEventType.TARGET_REACHED else HeaterCooledDown,
                extra_context={
                    'heater_name': event.state.name,
                    'heater_actual': event.state.actual,
                    'heater_target': event.state.target,
                    'heater_offset': event.state.offset,
                },
                img_url=None,
                print_=printer.current_print if printer.current_print_id else None,
            )

            if event.type == HeaterEventType.TARGET_REACHED:
                # Trying to save the moment when target first
                # reached for a (print, heater) pair.
                # This does not happen often.
                try:
                    PrintHeaterTarget.objects.create(
                        print_id=printer.current_print_id,
                        name=event.state.name,
                        target=event.state.target or 0.0,
                        offset=event.state.offset or 0.0,
                        created_at=new_updated_at,
                        updated_at=new_updated_at)
                except IntegrityError:
                    # means db has data already,
                    # all good
                    pass

    # removing obsolete entries
    if trackersd:
        HeaterTracker.objects.filter(
            printer=printer,
            name__in=[t.name for t in trackersd.values()],
        ).delete()

    return new_trackers


def process_heater_temps(printer: Printer, temps: Dict) -> int:
    now_ = now()
    qs = printer.heatertracker_set.all()
    MAX_TRIES = 2
    tries = 0

    # this is a hot path (in ws handler context), heater trackers are
    # cached in printer instance to avoid frequent db reads
    while True:
        try:
            if getattr(printer, '_heater_trackers', None) is None:
                # fill local cache
                printer._heater_trackers = list(qs)

            new_trackers = update_heater_trackers(
                printer,
                printer._heater_trackers,
                temps,
                now_=now_,
            )

            # update local cache
            printer._heater_trackers = new_trackers

            break
        except UpdateError:
            # local cache is considered invalid
            tries += 1
            if tries < MAX_TRIES:
                printer.refresh_from_db()
                printer._heater_trackers = None
            else:
                raise
    return tries
