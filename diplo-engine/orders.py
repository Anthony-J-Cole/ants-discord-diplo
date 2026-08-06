from dataclasses import dataclass
from typing import Optional

from .map import Map
from .state import GameState, Unit


# pseudo-oop  
@dataclass(frozen=True)
class Order:  
    unit: Unit


@dataclass(frozen=True)
class Hold(Order):
    # Do nothing, adjudicator handles
    pass


@dataclass(frozen=True)
class Move(order):
    destination: str
    # Currently putting here as rulebook states it is a move order
    is_convoy: bool = False

# Help defend 
@dataclass(frozen=True)
class SupportHold(Order):
    supported_unit: Unit

# Help attack
@dataclass(frozen=True)
class SupportMove(Order):
    supported_unit: Unit
    supported_dest: str

@dataclass(frozen=True)
class Convoy(Order):
    convoyed_unit: Unit
    convoyed_dest: str


class OrderError(ValueError):
    """Better here than stuck in a paradox"""


# If a valid order than keeps it, otherwise changes it to a hold
def validate_order(order: Order, game_map: Map, state: GameState) -> Order:
    unit = order.unit
    if state.units