from dataclasses import dataclass
from typing import Optional

from .day_type import DayType


@dataclass(frozen=True)
class Departure:
    stop_id: Optional[int]
    variant_id: int
    stop_index: int
    day_type: DayType
    hour: int
    minute: int

    def get_minutes(self):
        return self.hour * 60 + self.minute

    def time_distance_between(self, other: 'Departure'):
        minute_diff = other.get_minutes() - self.get_minutes()

        return minute_diff + 24 * 60 if minute_diff < 0 else minute_diff
