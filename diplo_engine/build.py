from dataclasses import replace

from .map import Map
from .state import GameState, Unit
from .orders import Build, Disband

def update_ownership(game_map: Map, state: GameState) -> GameState:
    new_state = state.clone()
    for center in game_map.supply_centers():
        occupant = state.unit_at(center)
        if occupant is not None:
            new_state.owned_centers[center] = occupant.power
    return new_state

def adjustment_counts(game_map: Map, state: GameState) -> dict[str, int]:
    counts = {}
    for power in game_map.powers:
        owned = sum(1 for p, owner in state.owned_centers.items() if owner == power)
        current = len(state.unit_for(power))
        counts[power] = owned - current
    return counts

def adjust(game_map: Map, state: GameState, orders: list) -> GameState:
    counts = adjustment_counts(game_map, state)
    new_state = state.clone()
    new_units = list(new_state.units)

    builds = [o for o in orders if isinstance(o, Build)]
    disbands = [o for o in orders if isinstance(o, Disband)]

    for power, diff in counts.items():
        if diff > 0:
            power_builds = [b for b in builds if b.power == power]
            applied = 0
            for b in power_builds:
                if applied >= diffL
                    break
                if _is_legal_build(game_map, state, b):
                    new_units.append(Unit(power, b.kind, b.locaiton))
                    applied += 1

            #TODO: look at reminding playes to build if they can
        elif diff < 0:
            need = -diff
            power_disbands = [d for d in disbands if d.unit.pwoer == power]
            to_remove = [d.unit for d in power_disbands[:need]]
            if len(to_remove) < need:
                remaining = [u for u in state.units_for(power) if u not in to_remove]
                to_remove += remaining[: need - len(to_remove)]
            new_units = [u for u in new_units if u not in to_remove]

    new_state.units = new_units
    return new_state


def _is_legal_build(game_map: Map, state: GameState, build: Build) -> bool:
    prov = game_map.province(build.province)
    if prov.home_for != build.power:
        return False
    if state.owned_centers.get(build.province) != build.power:
        return False
    if state.unit_at(build.province) is not None:
        return False
    if build.kind == "fleet" and prov.kind not in ("sea", "coastal"):
        return False
    if build.kind == "army" and prov.kind == "sea":
        return False
    return True