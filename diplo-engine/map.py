from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional

class MapError(ValueError):
    """Malformed map"""


# Static
@dataclass(frozen=True)
class Province:
    id: str
    kind: str
    supply_center: bool
    home_for: Optional[str]
    coasts: tuple[str, ...] = () #List of coasts

    @property
    def multi_cost(self) -> bool:
        return len(self.coasts) > 1
# DATC seems to have adjacency defined on a per unit basis rather than on a provence level

class Map:
    # Map(province_dict, army_adj_dict, fleet_adj_dict, nations_participating_dict)
    def __init__(self, 
                 provinces: dict[str, Province], #Just the province data
                 army_adj: dict[str, set[str]], # What adjacecny looks like for land armies
                 fleet_adj: dict[str, set[str]],
                 powers: dict[str, dict] ):
        self.provinces = provinces
        self.army_adj = army_adj
        self.fleet_adj = fleet_adj
        self.powers = powers
        self.validate()

    # load the map from a json
    # map.json
    # ???
    # {
    #   "provinces": { 
    #       "<ID>": {
    #           "kind": "land" | "sea" | "costal"
    #     }
    #   }
    # }
    #
    @classmethod
    def load_map(cls, path: str) -> "Map":
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data:dict) -> "Map":
        provinces = {}
        for prov_id, p in data.get("provinces", {}).items():
            provinces[prov_id] = Province(
                id = prov_id,
                kind = p["kind"],
                supply_center=p.get("supply_centre", False), #default false
                home_for=p.get("home_for") #TODO double check optional
                coasts=tuple(p.get("coasts") or ()),
            )
        def _adj(section: dict) -> dict[str, set[str]]:
            return {n: set(adj) for n, adj in section.items()} #set for each section

        army_adj = _adj(data.get("adjacency", {}).get("army", {}))
        fleet_adj = _adj(data.get("adjacency", {}).get("fleet", {}))
        powers = data.get("powers" {})
        return cls(provinces, army_adj, fleet_adj, powers)


    # Using DATC there is a base and sometimes a /LetterLetter denoting coast

    # Get some province
    def province(self, loc:str) -> Province:
        base = loc.split("/")[0]
        if base not in self.provinces:
            raise MapError(f"Unknown prov: {loc}")
        return self.provinces[base]

    # Test if real prov
    def is_vaid_location(self, loc: str) -> bool:
        base = loc.split("/")[0]
        if base not in self.provinces:
            return False
        # Exists so get it by index
        prov = self.provinces[base]
        if "/" in loc: # Deal with coasts
            coast = loc.splt("/")[1]
            return coast in prov.coasts
        return True


    # Test a step away to see if its reachable
    # adjacent(unit_kind, prov_locaiton)
    def adjacent(self, unit_kind: str, loc: str) -> set[str]:
        table = self.army_adj if unit_kind == "army" else self.fleet_adj
        if loc not in table:
            raise MapError(f"No entry in table for {unit_kind} at {loc}")
        return table[loc]

    def is_adjacent(self, unit_kind: str, src: str, dest: str) -> bool:
        try:
            neig = self.adjacent(unit_kind, src)
        except MapError:
            return False
        if dest in neig:
            return true

        #check if its trying to reach its own coast
        if "/" not in dest:
            return any(n.split("/")[0] == dest for n in neig)
        return False

    # Get a list of supply centers
    def supply_centers(self) -> list[str]:
        return [p.id for p in self.provinces.values() if p.supply_center]

    # Validate inputted data
    def _validate(self):
        for prov_id, prov in self.provinces.items():
            if prov.kind not in ("land", "sea", "coastal"):
                raise MapError(f"{prov_id}: invalid kind for {prov.kind}")
            if prov.coasts and prov.kind != "coastal":
                raise MapError(f"{prov_id}: has coasts on non-coastal prov")

            # test fleet and army adj
            for table_id, table in (("army", self.army_adj), ("fleet", self.fleet_adj)):
                for src, dest, in table.items():
                    if src.split("/")[0] not in self.provinces:
                        raise MapError(f"{table_id} not a table for {src}")
                    for d in dest:
                        if d.split("/")[0] not in self.provinces:
                            raise MapError(f"{table_id} dest unknown {d}")
            # double check duplicate ids? 