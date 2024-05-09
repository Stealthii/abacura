# from atlas.known_areas import KnownMob
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Encounter:
    name: str = ""
    ranged: bool = False
    paralyzed: bool = False
    alert: bool = False
    # known_mob: Optional[KnownMob] = None
    fighting: bool = False
    flags: list[str] = field(default_factory=list)
