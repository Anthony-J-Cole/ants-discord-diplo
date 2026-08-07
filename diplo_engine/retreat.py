from dataclasses import replace

from .map import Map
from .state import GameState, Unit
from .orders import Order, Retreat, Disband

def retreat(game_map: Map, state: GameState, orders:list[Order]) -> GameState:
    by_unit = {o.unit.location: o for o in orders}
    for province, unit in state.dislodged.items():
        by_unit.setdefault(unit.location, Disband(unit))

    # unit location - destination
    legal_moves: dict[str, str] = {}
    for province, unit in state.dislodged.items():
        order = by_unit.get(unit.location, Disband(unit))
        if not isinstance(order, Retreat):
            continue
        if _is_legal_retreat(game_map, state, unit, order.destination):
            legal_moves[unit.location] = order.destination

    dest_counts: dict[str, int] = {}
    for dest in legal_moves.values():
        dest_counts[dest.split("/")[0]] = dest_counts.get(dest.split("/")[0], 0) + 1

    new_state = state.clone()
    new_units = list(new_state.units)
    for province, unit in state.dislodged.items():
        dest = legal_moves.get(unit.location)
        if dest and dest_counts[dest.split("/")[0]] == 1:
            new_units.append(replace(unit, location=dest))

        # if not then the unit is not added to the next phase.
        # should stop most conflicts and paradoxes

    new_state.units = new_units
    new_state.dislodged = {}
    new_state.invalid_retreats = {}
    return new_state

def _is_legal_retreat(game_map: Map, state: GameState, unit: Unit, destination: str) -> bool:
    if not game_map.is_vaid_location(destination):
        return False
    if not game_map.is_adjacent(unit.kind, unit.location, destination):
        return False
    if state.unit_at(destination.split("/")[0]) is not None:
        return False
    forbidden = state.invalid_retreats.get(unit.province, set())
    if destination.split("/")[0] in forbidden:
        return False
    return True