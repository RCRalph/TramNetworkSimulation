from dataclasses import dataclass, field
from operator import indexOf

from .day_type import DayType
from .departure import Departure
from .tram_stop import TramStop


@dataclass
class TramPassage:
    line_id: int
    day: DayType
    reverse_stop_sequence: list[Departure] = field(default_factory=list)

    def add_stop(self, departure: Departure):
        self.reverse_stop_sequence.append(departure)

    def get_departure_index(self, departure: Departure) -> int:
        return indexOf(map(lambda x: x == departure, self.reverse_stop_sequence), True)

    def get_stop_names(self, tram_stops: dict[int, TramStop]):
        return [
            f"{item.hour:02d}:{item.minute:02d} {tram_stops[item.stop_id].name}"
            for item in reversed(self.reverse_stop_sequence)
        ]

    def __len__(self):
        return len(self.reverse_stop_sequence)
