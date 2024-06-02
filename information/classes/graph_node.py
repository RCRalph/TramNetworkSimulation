from dataclasses import dataclass, field
from decimal import Decimal
from geopy.distance import geodesic


@dataclass(frozen=True)
class GraphNode:
    id: int
    latitude: Decimal
    longitude: Decimal
    edges: list["GraphNode"] = field(default_factory=list, repr=False, hash=False)

    @property
    def coordinates(self):
        return (self.latitude, self.longitude)

    def distance_to(self, other: "GraphNode"):
        return geodesic(self.coordinates, other.coordinates).m
