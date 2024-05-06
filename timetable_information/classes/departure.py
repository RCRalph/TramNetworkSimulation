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

    def is_previous(self, other):
        if self.stop_index != other.stop_index - 1:
            return False

        return self.hour < other.hour or self.hour == other.hour and self.minute < other.minute
