import enum
import dataclasses
from typing import Dict, Optional, Any, List, Tuple, Set

from app.models import Printer, HeaterTracker
from lib.mobile_notifications import send_heater_event

COOLDOWN_THRESHOLD = 35.0  # degree celsius
TARGET_REACHED_DELTA = 3.0  # degree celsius


class HeaterEventType(enum.Enum):
    TARGET_REACHED = 'target reached'
    COOLED_DOWN = 'cooled down'


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
        name: HeaterState(name=name, target=v['target'], actual=v['actual'],
                          offset=v['offset'])
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
            )
            etype = heater.event_type_if_any()
            if etype is not None:
                tracker.reached = True
                event = HeaterEvent(type=etype, state=heater)

        ret.append((tracker, dirty, event))

    return ret


def update_heater_trackers(printer: Printer, temp_data: Dict) -> None:
    heaters = list(parse_states(temp_data).values())
    trackers = list(printer.heatertracker_set.all())
    trackersd = {tracker.name: tracker for tracker in trackers}

    changes = calc_changes(trackers, heaters)
    for tracker, dirty, event in changes:
        trackersd.pop(tracker.name, None)

        if dirty:
            tracker.printer = printer
            tracker.save()

        if event is not None:
            send_heater_event(
                printer,
                event=event.type_as_str(),
                heater_name=event.state.name,
                # 0.0 for pleasing mypy, actual cannot be None here
                actual_temperature=event.state.actual or 0.0)

    for obsolete_tracker in trackersd.values():
        obsolete_tracker.delete()
