import io
import logging

from PIL import Image, ImageDraw, ImageFont

from diplo_engine.map import Map
from diplo_engine.state import GameState

log = logging.getLogger(__name__)

_PALETTE = [
    (220, 60, 60), (60, 110, 220), (60, 170, 90), (230, 170, 30),
    (160, 80, 200), (40, 170, 170), (200, 100, 160), (120, 120, 120),
]
_SEA_COLOR = (200, 222, 240)
_LAND_COLOR = (235, 235, 225)
_LINE_COLOR = (160, 160, 160)
_MARGIN = 60
_RADIUS = 26

def _power_color(power: str, powers_in_order: list[str]) -> tuple[int, int, int]:
    idx = powers_in_order.index(power) if power in powers_in_order else hash(power)
    return _PALETTE[idx % len(_PALETTE)]
 
 
def render_png(game_map: Map, state: GameState) -> bytes:
    positioned = {p: prov for p, prov in game_map.provinces.items() if prov.position}
    skipped = set(game_map.provinces) - set(positioned)
    if skipped:
        log.warning(f"Skipping province with no location {sorted(skipped)}")
    if not positioned:
        raise ValueError("BAD")
 
    xs = [p.position[0] for p in positioned.values()]
    ys = [p.position[1] for p in positioned.values()]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    width = int(max_x - min_x + 2 * _MARGIN + 2 * _RADIUS)
    height = int(max_y - min_y + 2 * _MARGIN + 2 * _RADIUS)
 
    def to_canvas(pos):
        x, y = pos
        return (x - min_x + _MARGIN + _RADIUS, y - min_y + _MARGIN + _RADIUS)
 
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=13)
    except TypeError:
        font = ImageFont.load_default() 
 
    powers_in_order = sorted(game_map.powers)
 
    # Adjacency lines first, so provinces/units draw on top
    drawn_edges = set()
    for table in (game_map.army_adj, game_map.fleet_adj):
        for src, dsts in table.items():
            src_base = src.split("/")[0]
            if src_base not in positioned:
                continue
            for dst in dsts:
                dst_base = dst.split("/")[0]
                if dst_base not in positioned or dst_base == src_base:
                    continue
                edge = tuple(sorted((src_base, dst_base)))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)
                draw.line(
                    [to_canvas(positioned[src_base].position), to_canvas(positioned[dst_base].position)],
                    fill=_LINE_COLOR, width=2,
                )
 
    # Provinces
    for pid, prov in positioned.items():
        cx, cy = to_canvas(prov.position)
        fill = _SEA_COLOR if prov.kind == "sea" else _LAND_COLOR
        owner = state.owned_centers.get(pid)
        outline = _power_color(owner, powers_in_order) if owner else (90, 90, 90)
        outline_width = 4 if prov.supply_center else 2
        draw.ellipse(
            [cx - _RADIUS, cy - _RADIUS, cx + _RADIUS, cy + _RADIUS],
            fill=fill, outline=outline, width=outline_width,
        )
        draw.text((cx, cy + _RADIUS + 4), pid, fill=(30, 30, 30), font=font, anchor="ma")
 
    # Units - offset to see label
    for unit in state.units:
        base = unit.province
        if base not in positioned:
            continue
        cx, cy = to_canvas(positioned[base].position)
        color = _power_color(unit.power, powers_in_order)
        if unit.kind == "army":
            r = 9
            draw.rectangle([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(20, 20, 20))
        else:
            r = 10
            draw.polygon(
                [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)],
                fill=color, outline=(20, 20, 20),
            )
 
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
