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

    def look_for_event_type(self) -> Optional[HeaterEventType]:
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


def update_trackers(trackers: List[HeaterTracker],
                    heaters: List[HeaterState]) -> Tuple[List[HeaterTracker], List[HeaterEvent]]:
    trackersd = {t.name: t for t in trackers}
    events: List[HeaterEvent] = []
    seen: Set[str] = set()

    trackers_ = []
    for heater in heaters:
        if heater.name in seen:
            continue

        seen.add(heater.name)

        if heater.target is None:
            continue

        tracker = trackersd.pop(heater.name, None)
        if tracker is not None:
            if tracker.target == heater.target:
                if not tracker.reached:
                    type_ = heater.look_for_event_type()
                    if type_ is not None:
                        tracker.reached = True
                        events.append(HeaterEvent(type=type_, state=heater))
            else:
                tracker.target = heater.target
                tracker.reached = heater.look_for_event_type() is not None
        else:
            tracker = HeaterTracker(
                name=heater.name,
                target=heater.target,
                reached=heater.look_for_event_type() is not None
            )

        trackers_.append(tracker)

    return (trackers_, events)


def process_temp_data(printer: Printer, temp_data: Dict) -> None:
    heaters = list(parse_states(temp_data).values())
    trackers = list(printer.heatertracker_set.all())

    new_trackers, events = update_trackers(trackers, heaters)

    trackersd = {tracker.name: tracker for tracker in trackers}
    for tracker in new_trackers:
        trackersd.pop(tracker.name, None)
        if tracker.pk is None:
            tracker.save()

    for obsolete_tracker in trackersd.values():
        obsolete_tracker.delete()

    for e in events:
        send_heater_event(
            printer,
            event=e.type_as_str(),
            heater_name=e.state.name,
            # 0.0 for pleasing mypy, actual cannot be None here
            actual_temperature=e.state.actual or 0.0)
