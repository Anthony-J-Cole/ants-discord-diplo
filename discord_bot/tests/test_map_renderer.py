import os
import sys
 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
 
from diplo_engine.map import Map
from diplo_engine.state import GameState, Unit, Phase
from discord_bot.map_renderer import render_png
 
MAP_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "diplo_engine", "maps", "map_test.json"
)
 
 
def test_render_produces_valid_png():
    m = Map.load(MAP_PATH)
    state = GameState(
        map_name="test", phase=Phase.MOVEMENT, year=1901, season="spring",
        units=[Unit("france", "army", "PAR"), Unit("france", "army", "MAR"),
               Unit("italy", "army", "POR")],
        owned_centers={"PAR": "france", "MAR": "france", "POR": "italy"},
    )
    png_bytes = render_png(m, state)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"  # PNG file signature
    assert len(png_bytes) > 1000  # sanity check it's not a blank/degenerate image
    print(f"PASS: rendered a valid {len(png_bytes)}-byte PNG")
 
 
def test_render_handles_multicoast_and_sea():
    m = Map.load(MAP_PATH)
    state = GameState(
        map_name="test", phase=Phase.MOVEMENT, year=1901,
        units=[Unit("france", "fleet", "SPA/nc"), Unit("italy", "fleet", "MAO")],
    )
    png_bytes = render_png(m, state)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    print("PASS: renders fleets on multi-coast and sea provinces without error")
 
 
if __name__ == "__main__":
    test_render_produces_valid_png()
    test_render_handles_multicoast_and_sea()
 
    # also write one out so it can be visually inspected
    m = Map.load(MAP_PATH)
    state = GameState(
        map_name="test", phase=Phase.MOVEMENT, year=1901,
        units=[Unit("france", "army", "PAR"), Unit("france", "army", "MAR"),
               Unit("italy", "army", "POR"), Unit("france", "fleet", "WES")],
        owned_centers={"PAR": "france", "MAR": "france", "POR": "italy"},
    )
    with open("./test_map_render.png", "wb") as f:
        f.write(render_png(m, state))
 
