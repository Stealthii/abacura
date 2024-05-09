from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from abacura.plugins import ContextProvider
from abacura_kallisti.atlas.location import LocationList
from abacura_kallisti.atlas.room import ScannedRoom
from abacura_kallisti.atlas.world import World
from abacura_kallisti.metrics.odometer import Odometer
from abacura_kallisti.mud.msdp import TypedMSDP
from abacura_kallisti.mud.player import PlayerCharacter

if TYPE_CHECKING:
    from abacura.config import Config


class LOKContextProvider(ContextProvider):
    def __init__(self, config: Config, session_name: str) -> None:
        data_dir = Path(config.data_directory(session_name))
        super().__init__(config, session_name)
        self.world: World = World(data_dir / "world.db")
        self.msdp: TypedMSDP = TypedMSDP()
        self.pc: PlayerCharacter = PlayerCharacter()
        self.locations: LocationList = LocationList(data_dir / "locations.toml")
        self.room: ScannedRoom = ScannedRoom()
        self.odometer: Odometer = Odometer(self.msdp)

    def get_injections(self) -> dict:
        lok_context = {
            "world": self.world,
            "msdp": self.msdp,
            "pc": self.pc,
            "odometer": self.odometer,
            "locations": self.locations,
            "room": self.room,
        }

        return lok_context
