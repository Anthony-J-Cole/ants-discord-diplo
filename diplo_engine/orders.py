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
class Move(Order):
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
    if state.unit_at(unit.province) != unit:
        raise OrderError(f"Unit does not exist {unit}")
    # Check move
    if isinstance(order, Move):
        if order.is_convoy:
            return order # Too many conditions to check let the adjuicator handle it. 
        # Check moving to adjacent
        if not game_map.is_adjacent(unit.kind, unit.location, order.destination):
            # Not adjacent
            return Hold(unit)
        return order
    # Check SupportHold
    if isinstance(order, SupportHold):
        target = order.supported_unit.province
        if not game_map.is_adjacent(unit.kind, unit.location, target):
            return Hold(unit)
        return order
    # Check SupportMove
    if isinstance(order, SupportMove):
        target = order.supported_dest
        if not game_map.is_adjacent(unit.kind, unit.location, target):
            return Hold(unit)
        return order
    # Check Convoy
    if isinstance(order, Convoy):
        # cant convoy if not a fleet
        # cant convoy if not convoying over warter
        if unit.kind != "fleet" or game_map.province(unit.location).kind != "sea":
            return Hold(unit)
        return order
    #Hold case. 
    return order
