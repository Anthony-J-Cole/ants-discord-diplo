# VIBECODED with edits - Alot of manual data entry otherwise

"""
Generates standard.json — the full 75-province
classic Diplomacy board (7 powers, 34 supply centers).

This is a best-effort reconstruction of the standard board's geography
from well-established Diplomacy reference knowledge, not transcribed
from an official source file. Army adjacency and sea/coastal adjacency
are high-confidence. The trickiest part of ANY Diplomacy map — exactly
which coastal-province PAIRS share a coastline for fleet movement (as
opposed to just sharing a land border) — has some genuinely ambiguous
edge cases even among experienced implementers (Edinburgh/Clyde being
a classic example). Spot-check the FLEET_COASTAL edges below against a
canonical source (e.g. a DATC/judge map file) before running competitive
games on this.
"""
import json

POWERS = {
    "england": ["edi", "lvp", "lon"],
    "france": ["bre", "par", "mar"],
    "germany": ["kie", "ber", "mun"],
    "italy": ["ven", "rom", "nap"],
    "austria": ["vie", "tri", "bud"],
    "russia": ["stp", "mos", "war", "sev"],
    "turkey": ["ank", "con", "smy"],
}
# historical 1901 starting units — several are fleets, not armies, and Russia's
# St Petersburg fleet starts on a specific coast
STARTING_UNITS = {
    "england": [("fleet", "edi"), ("fleet", "lon"), ("army", "lvp")],
    "france": [("fleet", "bre"), ("army", "par"), ("army", "mar")],
    "germany": [("fleet", "kie"), ("army", "ber"), ("army", "mun")],
    "italy": [("army", "ven"), ("army", "rom"), ("fleet", "nap")],
    "austria": [("army", "vie"), ("fleet", "tri"), ("army", "bud")],
    "russia": [("army", "mos"), ("army", "war"), ("fleet", "stp/sc"), ("fleet", "sev")],
    "turkey": [("army", "con"), ("army", "smy"), ("fleet", "ank")],
}
NEUTRAL_SC = ["bel", "hol", "den", "nwy", "swe", "spa", "por", "tun", "gre", "ser", "rum", "bul"]

INLAND = {"par", "bur", "mun", "ruh", "sil", "boh", "tyr", "gal", "vie", "bud", "ser", "mos", "war", "ukr"}
SEAS = {"nao", "nwg", "bar", "nth", "eng", "iri", "mao", "wes", "lyo", "tys", "ion",
        "adr", "aeg", "eas", "bla", "bal", "bot", "ska", "hel"}
COASTS = {"stp": ("nc", "sc"), "spa": ("nc", "sc"), "bul": ("ec", "sc")}

ALL_LAND = set(INLAND) | {
    "cly", "edi", "lvp", "yor", "wal", "lon", "bre", "pic", "gas", "mar",
    "kie", "ber", "pru", "den", "nwy", "swe", "fin", "stp", "lvn", "sev",
    "tri", "rum", "bul", "gre", "alb", "pie", "tus", "ven", "rom", "nap",
    "apu", "tun", "con", "ank", "smy", "syr", "arm", "naf", "spa", "por",
    "bel", "hol",
}

POSITIONS = {
    "nao": (-60, 60), "cly": (40, 90), "edi": (95, 85), "nwg": (60, 20),
    "lvp": (60, 145), "yor": (125, 140), "wal": (60, 195), "lon": (125, 195),
    "nth": (175, 105), "eng": (140, 235), "iri": (5, 195),
    "bar": (300, -30), "nwy": (225, 35), "swe": (285, 70), "ska": (225, 100),
    "den": (225, 150), "hel": (190, 150), "bal": (275, 165), "fin": (345, 55),
    "stp": (425, 30), "bot": (335, 110), "lvn": (385, 145),
    "hol": (190, 190), "kie": (235, 190), "bel": (150, 230), "ruh": (200, 230),
    "ber": (285, 200), "mun": (230, 270), "pru": (335, 190), "sil": (300, 230),
    "bre": (70, 260), "pic": (140, 260), "par": (110, 300), "bur": (170, 300),
    "gas": (80, 330), "mar": (150, 350), "mao": (0, 300), "wes": (110, 450),
    "lyo": (170, 400),
    "war": (335, 260), "mos": (450, 220), "ukr": (395, 290), "gal": (325, 305),
    "sev": (455, 320), "rum": (400, 335),
    "boh": (270, 300), "vie": (300, 335), "tyr": (245, 340), "tri": (295, 385),
    "bud": (345, 345), "ser": (350, 390), "bul": (400, 415), "gre": (365, 450),
    "alb": (320, 425),
    "pie": (185, 350), "ven": (250, 375), "tus": (195, 400), "rom": (225, 435),
    "apu": (295, 435), "nap": (250, 465), "tys": (195, 475), "ion": (285, 480),
    "adr": (310, 410), "aeg": (415, 460), "eas": (450, 490),
    "con": (415, 425), "ank": (470, 420), "smy": (440, 465), "arm": (510, 400),
    "syr": (490, 490), "bla": (450, 375),
    "spa": (30, 380), "por": (-30, 380), "tun": (150, 480), "naf": (30, 470),
}

ARMY_EDGES = """
cly-edi cly-lvp edi-lvp edi-yor lvp-yor lvp-wal yor-wal yor-lon wal-lon
bre-pic bre-par bre-gas pic-par pic-bur pic-bel par-bur par-gas bur-gas
bur-mar bur-mun bur-ruh bur-bel gas-mar gas-spa mar-spa mar-pie
bel-bur bel-ruh bel-hol hol-ruh hol-kie ruh-kie ruh-mun kie-mun kie-ber
kie-den ber-mun ber-sil ber-pru mun-sil mun-boh mun-tyr sil-boh sil-gal
sil-pru sil-war pru-war
nwy-swe nwy-stp swe-fin fin-stp
stp-lvn stp-mos mos-lvn mos-war mos-ukr mos-sev lvn-war war-ukr war-gal
ukr-sev ukr-rum ukr-gal sev-arm sev-rum gal-boh gal-vie gal-rum gal-bud
vie-boh vie-bud vie-tri vie-tyr boh-tyr tyr-tri tyr-ven tyr-pie tri-bud
tri-ser tri-alb tri-ven bud-rum bud-ser
rum-ser rum-bul ser-bul ser-alb ser-gre bul-gre gre-alb
pie-ven pie-tus ven-tus ven-rom ven-apu tus-rom rom-apu rom-nap apu-nap
con-bul con-smy con-ank ank-smy ank-arm smy-arm smy-syr arm-syr
spa-por naf-tun
""".split()

# coastal province <-> coastal province, sharing an actual coastline (fleet-legal
# even though several of these ALSO appear disjoint from ARMY_EDGES is fine — the
# schema keys army/fleet separately on purpose)
FLEET_COASTAL = """
cly-edi cly-lvp lvp-wal wal-lon lon-yor yor-edi
bre-gas bre-pic pic-bel bel-hol hol-kie kie-den kie-ber ber-pru
den-swe swe-fin nwy-stp/nc stp/sc-fin nwy-swe stp/sc-lvn
mar-pie mar-spa/sc pie-tus tus-rom rom-nap nap-apu apu-ven ven-tri
tri-alb alb-gre gre-bul/sc bul/sc-con con-smy smy-syr bul/ec-con
bul/ec-rum rum-sev sev-arm arm-ank ank-con
naf-tun por-spa/nc gas-spa/nc
""".split()

# sea <-> sea, and sea <-> coastal-province(-or-coast)
FLEET_SEA = """
nao-nwg nao-iri nao-mao nao-cly nao-lvp
nwg-bar nwg-nth nwg-edi nwg-cly
bar-stp/nc bar-nwy
nth-eng nth-hel nth-ska nth-den nth-nwy nth-hol nth-edi nth-yor nth-lon
eng-iri eng-mao eng-bre eng-pic eng-bel eng-wal eng-lon
iri-mao iri-lvp iri-wal
mao-bre mao-gas mao-spa/nc mao-por mao-wes mao-naf
wes-spa/sc wes-lyo wes-tys wes-naf wes-tun
lyo-spa/sc lyo-mar lyo-pie lyo-tus lyo-tys
tys-tus tys-rom tys-nap tys-ion tys-tun
ion-nap ion-apu ion-adr ion-gre ion-alb ion-tun ion-eas
adr-tri adr-ven adr-apu adr-alb
aeg-gre aeg-bul/sc aeg-con aeg-smy aeg-ion aeg-eas
eas-smy eas-syr
bla-bul/ec bla-rum bla-sev bla-arm bla-ank bla-con
bal-den bal-kie bal-ber bal-pru bal-lvn bal-swe bal-bot
bot-swe bot-fin bot-stp/sc bot-lvn
ska-nwy ska-den ska-swe
hel-den hel-kie hel-hol
""".split()


# Changed original build to match my schema
def build():
    provinces = {}
    for pid in ALL_LAND | SEAS:
        if pid in SEAS:
            kind, sc, home = "sea", False, None
        else:
            kind = "land" if pid in INLAND else "coastal"
            sc = pid in [c for centers in POWERS.values() for c in centers] or pid in NEUTRAL_SC
            home = next((p for p, cs in POWERS.items() if pid in cs), None)
        provinces[pid.upper()] = {
            "kind": kind, "supply_center": sc, "home_for": home,
            "position": list(POSITIONS[pid]),
        }
        if pid in COASTS:
            provinces[pid.upper()]["coasts"] = list(COASTS[pid])

    def upper_loc(loc: str) -> str:
        # uppercase the province part, keep any /coast suffix lowercase
        if "/" in loc:
            prov, coast = loc.split("/")
            return f"{prov.upper()}/{coast}"
        return loc.upper()

    def add_edges(table: dict, edge_list: list[str]):
        for edge in edge_list:
            a, b = edge.split("-")
            a, b = upper_loc(a), upper_loc(b)
            table.setdefault(a, set()).add(b)
            table.setdefault(b, set()).add(a)

    army = {}
    add_edges(army, ARMY_EDGES)

    fleet = {}
    add_edges(fleet, FLEET_COASTAL)
    add_edges(fleet, FLEET_SEA)

    def sorted_table(t):
        return {k: sorted(v) for k, v in sorted(t.items())}

    powers = {
        p: {
            "home_centers": [c.upper() for c in cs],
            "starting_units": [[k, upper_loc(l)] for k, l in STARTING_UNITS[p]],
        }
        for p, cs in POWERS.items()
    }

    return {
        "provinces": provinces,
        "adjacency": {"army": sorted_table(army), "fleet": sorted_table(fleet)},
        "powers": powers,
    }


if __name__ == "__main__":
    data = build()
    with open("diplomacy_engine/maps/standard.json", "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    n_land = sum(1 for p in data["provinces"].values() if p["kind"] != "sea")
    n_sea = sum(1 for p in data["provinces"].values() if p["kind"] == "sea")
    n_sc = sum(1 for p in data["provinces"].values() if p["supply_center"])
    print(f"{len(data['provinces'])} provinces ({n_land} land, {n_sea} sea), {n_sc} supply centers")
