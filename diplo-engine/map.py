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