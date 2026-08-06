# Test that the engine and adjudicator works against DATC
# Probably wont ever pass in entirety but try to do some base tests 

import os
import sys

from diplo_engine.map import Map
from diplo_engine.state import GameState, Unit, Phase
from diplo_engine.orders import Hold, Move, SupportHold, SupportMove, Convoy
from diplo_engine.adjudicator import adjudicate

MAP_PATH = os.path.join(os.path.dirname(__file__), "maps", "map_test.json")


def load_map():
    return Map.load(MAP_PATH)

def base_state(units):
    return GameState(map_name="test", phase=Phase.MOVEMENT, year=1901, units=list(units))

def test_unopposed_move():
    m = load_map()
    unit = Unit("france", "army", "PAR")
    state = base_state([unit])
    result = adjudicate(m, state, [Move(unit, "BUR")])

    assert result.unit_at("BUR") is not None
    assert result.unit_at("PAR") is None
    print("PASS: unopposed move")

def test_bounce_equal_strength():
    m = load_map()
    a = Unit("france", "army", "PAR")
    b = Unit("Germany", "army", "BUR")
    state = base_state([a, b])
    orders = [Move(a, "BUR"), Move(b, "PAR")]
    result = adjudicate(m, state, orders)

    # Both bounce
    assert result.unit_at("BUR") == a
    assert result.unit_at("BUR") == b
    print ("PASS: bounce")


def test_support_wins_and_dislodges():
    m = load_map()
    a = Unit("france", "army", "PAR")
    s = Unit("france", "army", "GAS")
    d = Unit("germany", "army", "BUR")
    state = base_state([a, s, d])
    orders = [
        Move(a, "BUR"),
        SupportMove(s, a, "BUR"),
        Hold(d),
    ]
    result = adjudicate(m, state, orders)

    assert result.unit_at("BUR").power == "france"
    assert "BUR" in result.dislodged
    assert result.dislodged["BUR"] == d
    print("PASS: supported attack dislodges defender")

def test_support_is_cut():
    m = load_map()
    attacker = Unit("france", "army", "PAR")
    supporter = Unit("france", "army", "GAS")
    defender = Unit("germany", "army", "BUR")
    cutter = Unit("germany", "army", "SPA")
    state = base_state([attacker, supporter, defender, cutter])
    orders = [
        Move(attacker, "BUR"),
        SupportMove(supporter, attacker, "BUR"),
        Hold(defender),
        Move(cutter, "GAS"),  # cuts the support
    ]
    result = adjudicate(m, state, orders)

    # Support cut so bounce 
    assert result.unit_at("PAR") == attacker
    assert result.unit_at("BUR") == defender
    print("PASS: support correctly cut")
 
 
def test_convoy_path():
    m = load_map()
    army = Unit("france", "army", "POR")
    fleet1 = Unit("france", "fleet", "MAO")
    fleet2 = Unit("france", "fleet", "WES")
    state = base_state([army, fleet1, fleet2])
    orders = [
        Move(army, "MAR", via_convoy=True),
        Convoy(fleet1, army, "MAR"),
        Convoy(fleet2, army, "MAR"),
    ]
    result = adjudicate(m, state, orders)

    assert result.unit_at("MAR") is not None
    assert result.unit_at("MAR").power == "france"
    assert result.unit_at("POR") is None
    print("PASS: multi-hop convoy path resolves")
 
 
def test_five_unit_circular_rotation():
    m = load_map()
    units = {
        "PAR": Unit("france", "army", "PAR"),
        "BUR": Unit("germany", "army", "BUR"),
        "MAR": Unit("italy", "army", "MAR"),
        "SPA": Unit("spain", "army", "SPA"),
        "GAS": Unit("england", "army", "GAS"),
    }
    state = base_state(units.values())
    orders = [
        Move(units["PAR"], "BUR"),
        Move(units["BUR"], "MAR"),
        Move(units["MAR"], "SPA"),
        Move(units["SPA"], "GAS"),
        Move(units["GAS"], "PAR"),
    ]
    result = adjudicate(m, state, orders)

    assert result.unit_at("BUR").power == "france"
    assert result.unit_at("MAR").power == "germany"
    assert result.unit_at("SPA").power == "italy"
    assert result.unit_at("GAS").power == "spain"
    assert result.unit_at("PAR").power == "england"
    print("PASS: five-unit circular rotation resolves")
 
 
if __name__ == "__main__":
    test_unopposed_move()
    test_bounce_equal_strength()
    test_support_wins_and_dislodges()
    test_support_is_cut()
    test_convoy_path()
    test_five_unit_circular_rotation()
    print("\nAll tests passed.")
