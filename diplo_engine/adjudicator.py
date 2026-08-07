# Simple cases.

# To future me: good luck.

from collections import deque
from dataclasses import replace

from .map import Map
from .state import GameState, Unit
from .orders import Order, Hold, Move, SupportHold, SupportMove, Convoy

# Take in a map, a gamestate and a list of orders and return a game state
def adjudicate(game_map: Map, state: GameState, orders: list[Order]) -> GameState:
    # Handle orders on a per unit basis
    by_unit = {o.unit.location: o for o in orders}
    for u in state.units:
        # If a unit doesnt have a order. Set it to hold
        by_unit.setdefault(u.location, Hold(u))

    orders = list(by_unit.values())
    valid_orders = _resolve_convoy_validity(game_map, orders)
    cut_support = _compute_support_cuts(valid_orders)
    winners, dislodged, standoffs = _resolve_movement(valid_orders, cut_support)

    # Apply to GameState
    return _apply_results(state, orders, winners, dislodged, standoffs)


def _resolve_convoy_validity(game_map: Map, orders: list[Order]) -> list[Order]:
    convoy_orders = [o for o in orders if isinstance(o, Convoy)]
    result = []
    for o in orders:
        if isinstance(o, Move) and o.is_convoy:
            valid_path = _convoy_path_exists(game_map, convoy_orders, o.unit.province, o.destination)
            result.append(o if valid_path else Hold(o.unit))
        else:
            result.append(o)
    return result

# Breath first search 
def _convoy_path_exists(game_map: Map, convoy_orders: list[Convoy], source: str, dest: str) -> bool:
    active = {
        c_order.unit.province for c_order in convoy_orders
        if c_order.convoyed_dest.split("/")[0] == dest.split("/")[0]
    }

    if not active:
        return False

    start = {p.split("/")[0] for p in game_map.adjacent("fleet", source)} & active
    visited = set()
    frontier = deque(start)
    while frontier:
        base = frontier.popleft()
        if base in visited:
            continue
        visited.add(base)
        neighbors = {p.split("/")[0] for p in game_map.adjacent("fleet", base)}
        if dest.split("/")[0] in neighbors:
            return True
        for next in neighbors & active:
            if next not in visited:
                frontier.append(next)
    return False

# Return prov where units get support cut
def _compute_support_cuts(orders: list[Order]) -> set[str]:
    moves = [order for order in orders if isinstance(order, Move)]
    cut = set()
    for o in orders:
        if not isinstance(o, (SupportHold, SupportMove)):
            continue
        for move in moves:
            if move.destination.split("/")[0] != o.unit.province:
                continue
            # Support is not cut if the attack is from the supported units attack target
            if isinstance(o, SupportMove) and move.unit.province == o.supported_dest.split("/")[0]:
                continue
            cut.add(o.unit.location)
            break
    return cut


def _strength(order: Order, all_orders: list[Order], cut: set[str]) -> int:
    supports = 0
    for o in all_orders:
        if o.unit.location in cut:
            continue
        # Support attack
        if isinstance(order, Move) and isinstance(o, SupportMove):
            if (o.supported_unit.location == order.unit.location and 
                o.supported_dest.split("/")[0] == order.destination.split("/")[0]):
                supports += 1
        # Support hold
        elif not isinstance(order, Move) and isinstance(o, SupportHold):
            if o.supported_unit.location == order.unit.location:
                supports += 1
    # A unit is always supporting itself
    return 1 + supports

def _resolve_movement(orders:list[Order], cut: set[str]):
    moves = [o for o in orders if isinstance(o, Move)]

    # Assume every move succeeds so A->B, B->C, C->A 
    # If a move fails it needs to change to defending itself 

    status: dict[str, bool] = {m.unit.location: True for m in moves}
    for _ in range(len(orders) + 1):
        changed = False
        occupied_after = _current_occupant(orders, status)

        for m in moves: 
            dest = m.destination.split("/")[0]
            attack_str = _strength(m, orders, cut)

            # Starts attack against prov already occupied
            opposing = next((o for o in moves if o.unit.location == m.destination 
            and o.destination.split("/")[0] == m.unit.province), None, )

            if opposing:
                opp_strength = _strength(opposing, orders, cut)
                result = attack_str > opp_strength

            # Starts contested attack against prov that is empty
            else:
                defender = occupied_after.get(dest)
                if defender is None:
                    rivals = [o for o in moves if o is not m and o.destination.split("/")[0] == dest]
                    winning_rival = max((_strength(r, orders, cut) for r in rivals), default=0)
                    result = attack_str > winning_rival
                else:
                    defend_str = _strength(defender, orders, cut)
                    result = attack_str > defend_str
            prev = status.get(m.unit.location)
            if prev != result:
                changed = True
            status[m.unit.location] = result
        if not changed:
            break

    dislodged = {}
    winners = status
    for m in moves:
        if status.get(m.unit.location):
            dest = m.destination.split("/")[0]
            stayer = _stationary_unit_at(orders, dest, status)
            if stayer is not None:
                dislodged[dest] = (stayer, m.unit.province)  # unit, attacker's origin
 
    standoffs = {
        m.destination.split("/")[0] for m in moves if status.get(m.unit.location) is False
    }
    return winners, dislodged, standoffs


def _current_occupant(orders: list[Order], status: dict[str, bool]):
    occ = {}
    for o in orders:
        if isinstance(o, Move) and status.get(o.unit.location) is True:
            continue
        occ[o.unit.province] = o
    return occ

def _stationary_unit_at(orders: list[Order], province: str, status: dict[str, bool]) -> Unit | None:
    for o in orders: 
        if o.unit.province != province:
            continue
        if isinstance(o, Move) and status.get(o.unit.location):
            # Successful move away, no unit was dislodged
            return None
        return o.unit
    return None

def _apply_results(state: GameState, orders: list[Order], winners: dict[str, bool],
                    dislodged: dict[str, tuple[Unit, str]], standoffs: set[str]) -> GameState:
    new_state = state.clone()
    new_state.dislodged = {}
    new_state.invalid_retreats = {}
    new_units = []
    for o in orders:
        if isinstance(o, Move) and winners.get(o.unit.location):
            new_units.append(replace(o.unit, location=o.destination))
        elif o.unit.province in dislodged and dislodged[o.unit.province][0] == o.unit:
            unit, attacker_origin = dislodged[o.unit.province]
            new_state.dislodged[o.unit.province] = unit
            new_state.invalid_retreats[o.unit.province] = {attacker_origin} | standoffs
        else:
            new_units.append(o.unit)
    new_state.units = new_units
    return new_state
