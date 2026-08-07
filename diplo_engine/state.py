from dataclasses import dataclass, field
from enum import Enum

# Idea is to have state be datastructres. 
# Have a adjudicator take the orders and returns GameState.

# Two static gamestates that alternate? 
# Fall/Spring?


class Phase(Enum):
    MOVEMENT = "movement"
    RETREAT = "retreat"
    BUILD = "build"


@dataclass(frozen=True)
class Unit:
    power: str
    kind: str
    location: str # prov-id 

    # Get true prov if fleet 
    @property
    def province(self) -> str:
        return self.location.split("/")[0]

@dataclass
class GameState:
    map_name: str
    phase: Phase
    year: int
    units: list[Unit] = field(default_factory=list) # not shared mut. 
    #TODO: rego through field
    owned_centers: dict[str, str] = field(default_factory=dict) # who owns what prov - power
    dislodged: dict[str, Unit] = field(default_factory=dict) # units that are dislodged
    invalid_retreats: dict[str, set[str]] = field(default_factory=dict)
    # Invalid retreats may be a whole thing and need more in the future.
    # TODO go through: https://petermc.net/diplomacy/datc_v3_2.html#4.A

    
    # Check that a unit is at a province
    def unit_at(self, prov: str) -> Unit | None:
        for unit in self.units:
            if unit.province == prov:
                return unit
        return None

    # Gets units targeted via power 
    def units_for(self, power: str) -> list[Unit]:
        return [u for u in self.units if u.power == power]

    def clone(self) -> "GameState":
        return GameState(
            map_name=self.map_name,
            phase=self.phase, 
            year=self.year,
            units=list(self.units),
            owned_centers=dict(self.owned_centers),
            dislodged=dict(self.dislodged),
            invalid_retreats={i: set(j) for i, j in self.invalid_retreats.items()},
        )