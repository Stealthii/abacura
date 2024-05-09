from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Affect:
    name: str
    hours: int
