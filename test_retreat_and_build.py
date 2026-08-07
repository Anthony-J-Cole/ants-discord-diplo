import os
import sys

from diplo_engine.map import Map
from diplo_engine.state import GameState, Unit, Phase
from diplo_engine.orders import Build, Disband, Retreat
from diplo_engine.retreat import retreat
from diplo_engine.build import update_ownership, adjust, adjustment_counts
 
MAP_PATH = os.path.join(os.path.dirname(__file__), "maps", "map_test.json")
 
 
def load_map():
    return Map.load(MAP_PATH)
 
 
def base_state(units, dislodged=None, invalid=None, owned=None):
    return GameState(
        map_name="demo", phase=Phase.RETREAT, year=1901,
        units=list(units),
        dislodged=dict(dislodged or {}),
        invalid_retreats=dict(invalid or {}),
        owned_centers=dict(owned or {}),
    )
 
def test_legal_retreat_succeeds():
    m = load_map()
    dislodged_unit = Unit("germany", "army", "BUR")
    survivor = Unit("france", "army", "PAR")
    state = base_state(
        [survivor],
        dislodged={"BUR": dislodged_unit},
        invalid={"BUR": {"PAR"}},
    result = retreat(m, state, [Retreat(dislodged_unit, "MAR")])

    assert result.unit_at("MAR") is not None
    assert result.unit_at("MAR").power == "germany"
    assert result.dislodged == {}
    print("PASS: legal retreat succeeds")
 
 
def test_retreat_to_attacker_origin_is_illegal():
    m = load_map()
    dislodged_unit = Unit("germany", "army", "BUR")
    survivor = Unit("france", "army", "PAR")
    state = base_state(
        [survivor],
        dislodged={"BUR": dislodged_unit},
        invalid={"BUR": {"PAR"}},
    )
    result = retreat(m, state, [Retreat(dislodged_unit, "PAR")])

    assert result.unit_at("PAR") == survivor  # blocked
    assert all(u.power != "germany" for u in result.units)
    # Expect that they get disbanded 
    print("PASS: retreat into attacker's origin is invalid")
 
 
def test_retreat_standoff_disbands_both():
    m = load_map()
    unit_a = Unit("germany", "army", "BUR")
    unit_b = Unit("italy", "army", "SPA")
    state = base_state(
        [],
        dislodged={"BUR": unit_a, "SPA": unit_b},
        invalid={"BUR": set(), "SPA": set()},
    )
    orders = [Retreat(unit_a, "MAR"), Retreat(unit_b, "MAR")]
    result = retreat(m, state, orders)

    assert result.unit_at("MAR") is None
    assert len(result.units) == 0
    print("PASS: two units retreating to the same province both disband")
 
 
def test_no_order_disbands():
    m = load_map()
    unit = Unit("germany", "army", "BUR")
    state = base_state([], dislodged={"BUR": unit}, invalid={"BUR": set()})
    result = retreat(m, state, [])

    assert len(result.units) == 0
    print("PASS: dislodged unit with no retreat order is disbanded")
 
  
def test_ownership_updates_on_occupation():
    m = load_map()
    unit = Unit("france", "army", "MAR")
    state = base_state([unit])
    result = update_ownership(m, state)
    assert result.owned_centers["MAR"] == "france"
    print("PASS: ownership updates from occupation")
 
 
def test_build_when_centers_exceed_units():
    m = load_map()
    state = base_state(
        [Unit("france", "army", "PAR")],
        owned={"PAR": "france", "MAR": "france"},
    )
    counts = adjustment_counts(m, state)
    assert counts["france"] == 1  # 2 centers, 1 unit. Can build 1
    result = adjust(m, state, [Build("france", "army", "MAR")])

    assert result.unit_at("MAR") is not None
    assert len(result.units) == 2
    print("PASS: build applies when centers exceed units")
 
 
def test_illegal_build_site_is_rejected():
    m = load_map()
    state = base_state(
        [Unit("france", "army", "PAR")],
        owned={"PAR": "france", "MAR": "france"},
    )
    # POR is a supply center but not a french home center
    result = adjust(m, state, [Build("france", "army", "POR")])

    assert result.unit_at("POR") is None
    assert len(result.units) == 1  # build slot forfeited
    print("PASS: build in a non-home center is rejected")
 
 
def test_disband_when_units_exceed_centers():
    m = load_map()
    state = base_state(
        [Unit("france", "army", "PAR"), Unit("france", "army", "MAR")],
        owned={"PAR": "france"},  # 2 units 1 center. Must disband 1
    )
    result = adjust(m, state, [Disband(Unit("france", "army", "MAR"))])

    assert len(result.units_for("france")) == 1
    assert result.unit_at("PAR") is not None
    print("PASS: disband applies when units exceed centers")
 
 
def test_disband_fallback_when_no_order_given():
    m = load_map()
    state = base_state(
        [Unit("france", "army", "PAR"), Unit("france", "army", "MAR")],
        owned={"PAR": "france"},
    )
    result = adjust(m, state, [])  # no disband order submitted at all
    
    assert len(result.units_for("france")) == 1
    print("PASS: fallback disbands when no order is given")
 
 
if __name__ == "__main__":
    test_legal_retreat_succeeds()
    test_retreat_to_attacker_origin_is_illegal()
    test_retreat_standoff_disbands_both()
    test_no_order_disbands()
    test_ownership_updates_on_occupation()
    test_build_when_centers_exceed_units()
    test_illegal_build_site_is_rejected()
    test_disband_when_units_exceed_centers()
    test_disband_fallback_when_no_order_given()
    print("\nAll tests passed.")
