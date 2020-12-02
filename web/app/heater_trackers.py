import enum
import dataclasses
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple, Set
import logging

from app.models import Printer, HeaterTrackers
from lib.mobile_notifications import send_heater_event
from django.utils.timezone import now

COOLDOWN_THRESHOLD = 35.0  # degree celsius
TARGET_REACHED_DELTA = 3.0  # degree celsius


class UpdateError(Exception):
    pass


class HeaterEventType(enum.Enum):
    TARGET_REACHED = 'target reached'
    COOLED_DOWN = 'cooled down'


@dataclasses.dataclass
class HeaterTracker:
    name: str
    target: float
    reached: bool


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


def parse_trackers(data: List[Dict[str, Any]]) -> List[HeaterTracker]:
    """
    [{'name': 'tool0', 'target': 90.0, reached: true}, ...]
    """
    return [
        HeaterTracker(name=v['name'], target=v['target'], reached=v['reached'])
        for v in data
    ]


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


def process_heater_temps(printer: Printer, temps: Dict) -> int:
    MAX_TRIES = 2
    tries = 0

    # this is a hot path (in ws handler context), heater trackers are
    # cached in printer instance to avoid frequent db reads
    while True:
        try:
            if not hasattr(printer, 'heatertrackers'):
                obj, _ = HeaterTrackers.objects.get_or_create(printer=printer, defaults={'data': []})
                setattr(printer, 'heatertrackers', obj)

            heaters = list(parse_states(temps).values())
            trackers = parse_trackers(printer.heatertrackers.data)
            changes = calc_changes(trackers, heaters)
            dirty = any([x[1] for x in changes]) or len(changes) != len(trackers)
            if dirty:
                new_trackers = [x[0] for x in changes]
                new_data = [dataclasses.asdict(t) for t in new_trackers]

                touched = HeaterTrackers.objects.filter(
                    printer=printer,
                    updated_at=printer.heatertrackers.updated_at,
                ).update(
                    data=new_data,
                    updated_at=now()
                )

                if not touched:
                    raise UpdateError()

                printer.heatertrackers.data = new_data

                events = [x[2] for x in changes if x[2] is not None]
                for event in events:
                    send_heater_event(
                        printer,
                        event=event.type_as_str(),
                        heater_name=event.state.name,
                        # 0.0 for pleasing mypy, actual cannot be None here
                        actual_temperature=event.state.actual or 0.0)

            break
        except UpdateError:
            # local cache is considered invalid
            tries += 1
            if tries < MAX_TRIES:
                printer.refresh_from_db()
                printer.heatertrackers = None
            else:
                logging.error("could not update heater trackers")
                break  # or raise ?  # FIXME
    return tries
