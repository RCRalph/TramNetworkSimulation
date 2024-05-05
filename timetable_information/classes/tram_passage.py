from dataclasses import dataclass, field
from operator import indexOf

from .day_type import DayType
from .tram_stop import TramStop


@dataclass
class PassageStop:
    departure_id: int
    stop_id: TramStop
    hour: int
    minute: int


@dataclass
class TramPassage:
    line_id: int
    day: DayType
    reverse_stop_sequence: list[PassageStop] = field(default_factory=list)

    def add_stop(self, departure_id: int, tram_stop: TramStop, hour: int, minute: int):
        self.reverse_stop_sequence.append(PassageStop(departure_id, tram_stop, hour, minute))

    def get_departure_index(self, departure_id: int) -> int:
        return indexOf(map(lambda x: x.departure_id == departure_id, self.reverse_stop_sequence), True)

    def __len__(self):
        return len(self.reverse_stop_sequence)
