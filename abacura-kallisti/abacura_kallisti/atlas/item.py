from dataclasses import dataclass


@dataclass
class Item:
    name: str = ""
    blue: bool = False
    count: int = 0
    # flags: List[str] = field(default_factory=List)
