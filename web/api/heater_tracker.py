import enum
import dataclasses
from typing import Dict, Optional, Any, List

from app.models import Printer

COOLDOWN_THRESHOLD = 35.0  # degree celsius
TARGET_REACHED_DELTA = 3.0  # degree celsius


class HeaterEventType(enum.Enum):
    TARGET_REACHED = 'target_reached'
    COOLED_DOWN = 'cooled_down'


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


def parse(d: Dict[str, Dict[str, Any]]) -> Dict[str, HeaterState]:
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


def look_for_events(tracked_heaters: List[str],
                    temperature_data: Dict) -> List[HeaterEvent]:
    heaters = parse(temperature_data)
    events: List[HeaterEvent] = []
    for name in tracked_heaters:
        heater = heaters.get(name)
        if heater is not None:
            t = heater.look_for_event_type()
            if t is not None:
                events.append(HeaterEvent(type=t, state=heater))
    return events
