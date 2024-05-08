from dataclasses import dataclass

from abacura.plugins.events import AbacuraMessage

from .room import Room
from .world import World


@dataclass
class MapUpdateMessage(AbacuraMessage):
    start_room: Room | None = None
    current_vnum: str = ""
    world: World | None = None
    traveling: bool = False
    wilderness: bool = False
    ship: bool = False
    event_type: str = "lok.map.update"


@dataclass
class MapUpdateRequest(AbacuraMessage):
    event_type: str = "lok.map.update_request"
