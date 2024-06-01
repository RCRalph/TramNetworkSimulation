from dataclasses import dataclass, field
from decimal import Decimal
from math import sqrt

@dataclass(frozen=True)
class GraphNode:
    id: int
    latitude: Decimal
    longitude: Decimal
    edges: list["GraphNode"] = field(default_factory=list, repr=False, hash=False)

    def distance_to(self, other: "GraphNode"):
        return sqrt(float((self.latitude - other.latitude)**2 + (self.longitude - other.longitude)**2))
    
    @property
    def coordinates(self):
        return (self.latitude, self.longitude)