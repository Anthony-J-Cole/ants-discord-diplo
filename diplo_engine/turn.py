from .map import Map
from .state import GameState, Phase
from .adjudicator import adjudicate
from .retreat import retreat as resolve_retreat
from .build import update_ownership, adjust

def phase_key(state: GameState) -> str:
    return f"{state.year}-{state.season}-{state.phase.value}"

def process_phase(game_map: Map, state: GameState, orders: list) -> GameState:
    if state.phase == Phase.MOVEMENT:
        new_state = adjudicate(game_map, state, orders)
        if new_state.dislodged:
            new_state.phase = Phase.RETREAT
        else:
            new_state = _advance_past_movement(game_map, new_state)
        return new_state

    if state.phase == Phase.RETREAT:
        new_state = resolve_retreat(game_map, state, orders)
        return _advance_past_movement(game_map, new_state)

    if state.phase == Phase.BUILD:
        new_state = adjust(game_map, state, orders)
        new_state.year += 1
        new_state.season = "spring"
        new_state.phase = Phase.MOVEMENT
        return new_state

    raise ValueError(f"Unknown phase: {state.phase}")

def _advance_past_movement(game_map: Map, state: GameState) -> GameState:
    if state.season == "spring":
        state.season = "fall"
        state.phase = Phase.MOVEMENT
    else:
        state = update_ownership(game_map, state)
        state.phase = Phase.BUILD
    return state