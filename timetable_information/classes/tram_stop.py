from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TramStop:
    """
        TramStop class represents a tram stop. Tram stops are considered equal
        when their names are the same. In case of multiple stops with the same name,
        their locations should be close enough to not make a difference in the model,
        and they would be difficult to distinguish between each other using the
        data available from the timetable.
    """

    node_id: int
    name: str
    latitude: Decimal
    longitude: Decimal

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TramStop):
            return False

        return self.name == other.name

    def to_dict(self) -> dict[str, int | str | tuple[float, float]]:
        return {
            "id": self.node_id,
            "name": self.name,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude)
        }

    def to_sql_parameters(self) -> tuple[int, str, float, float]:
        return (
            self.node_id,
            self.name,
            float(self.latitude),
            float(self.longitude)
        )
