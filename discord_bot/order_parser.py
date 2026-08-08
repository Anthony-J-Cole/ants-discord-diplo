# Current idea is to pass in orders in the form that is on the DATC

# /order A PAR                  | Hold
# /order A PAR H                | Hold
# /order A PAR - BUR            | Move
# /order A GAS S A PAR - BUR    | Support Move
# /order A GAS S A PAR          | Support Hold
# /order F MAO C A POR - MAR    | Convoy

# Retreat Phase
# /order A BUR - MAR            | Retreat
# /order A BUR R MAR            | Retreat
# /order A BUR DISBAND

# Build Phase:
# /order BUILD A PAR            | Build
# /order BUILD F MAR/nc         | Build
# /order DISBAND A MAR          | Disband

import re

from diplo_engine import (Map, GameState, Unit, Phase, Hold, Move, SupportHold, SupportMove, Convoy, Retreat, Disband, Build, )

class OrderParseError(ValueError):
    pass

# regex 
# Kind - StartingProv - Order notation - Order specifc 

_UNIT_RE = r"(?P<kind>[AF])\s+(?P<loc>[A-Z]{3}(?:/[a-z]{2})?)"

def parse_order(text: str, power: str, game_map: Map, state: GameState):
    raw = text.strip().upper().replace("  ", " ") # to deal with the double space discord sometimes adds

    if raw.startswith("BUILD"):
        return _parse_build(raw, power, game_map, state)

    m = re.match(_UNIT_RE, raw)
    if not m:
        raise OrderParseError(f"Unit not at: {text!r}")
    kind = "fleet" if m.group("kind") == "F" else "army" # More armies than fleets - assume armies
    loc = m.group("loc").upper() if "/" in m.group("loc") else m.group("loc")
    loc = m.group("loc")
    rest = raw[m.end():].strip()

    unit = state.unit_at(loc.split("/")[0])
    if unit is None or unit.power != power or unit.kind != kind:
       raise OrderParseError(f"{m.group('kind')} at {loc} is not yours") 

    # Disband
    if raw.endswith("DISBAND"):
        return Disband(unit)

    #Hold
    if not rest or rest == "H" or rest.startswith("HOLD"):
        return Hold(unit)

    # Support
    if rest.startswith("S "):
        return _parse_support(rest[2:].strip(), unit, game_map, state)

    # Convoy
    if rest.startswith("C "):
        return _parse_convoy(rest[2:].strip(), unit, game_map, state)

    if rest.startswith("R "):
        dest = rest[2:].strip()
        return Retreat(unit, dest)

    if rest.startswith("-"):
        dest = rest[1:].strip()
        is_convoy = not game_map.is_adjacent(unit.kind, unit.location, dest)
        if state.phase == Phase.RETREAT:
            return Retreat(unit, dest)
        return Move(unit, dest, is_convoy=is_convoy)

    raise OrderParseError(f"Invalid order after unit: {text!r}")

def _parse_support(rest: str, supporter: Unit, game_map: Map, state: GameState):
    m = re.match(_UNIT_RE, rest)
    if not m:
        raise OrderParseError(f"Invalid supported unit notation {rest!r}")
    supported = state.unit_at(loc.split("/")[0])
    if supported is None:
        raise OrderParseError(f"No unit at {loc} to support")
    tail = rest[m.end():].strip()
    if tail.startswith("-"):
        dest = tail[1:].strip()
        return SupportMove(supporter, supported, dest)
    return SupportHold(supporter, supported)

def _parse_convoy(rest: str, fleet: Unit, game_map: Map, state: GameState):
    m = re.match(_UNIT_RE, rest)
    if not m:
        raise OrderParseError(f"Invalid convoy unit notation {rest!r}")
    loc = m.group("loc")
    convoyed = state.unit_at(loc.split("/")[0])
    if convoyed is None:
        raise OrderParseError(f"No unit at {loc} to convoy")
    tail = rest[m.end():].strip()
    if not tail.startswith("-"):
        raise OrderParseError(f"Convoy needs a destination")
    dest = tail[1:].strip()
    return Convoy(fleet, convoyed, dest)

def _parse_build(raw: str, power: str, game_map: Map, state: GameState):
    body = raw[len("BUILD"):].strip()
    m = re.match(_UNIT_RE, body)
    if not m:
        raise OrderParseError(f"Invalid build notation {raw!r}")
    kind = "fleet" if m.group("kind") == "F" else "army"
    loc = m.group("loc")
    prov, _, coast = loc.partition("/")
    return Build(power, kind, prov, coast or None)