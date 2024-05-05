from enum import Enum


class DayType(Enum):
    WEEKDAY = 'W'
    SATURDAY = 'S'
    HOLIDAY = 'H'

    @classmethod
    def values(cls):
        return [item.value for item in cls]
