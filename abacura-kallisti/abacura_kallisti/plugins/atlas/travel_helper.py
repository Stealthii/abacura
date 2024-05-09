from __future__ import annotations

import time
from typing import TYPE_CHECKING

from abacura.plugins import command
from abacura.utils.renderables import AbacuraPanel, Group, OutputColors, Text, tabulate
from abacura_kallisti.atlas.travel_guide import TravelGuide
from abacura_kallisti.plugins import LOKPlugin
from abacura_kallisti.plugins.scripts.travel import TravelRequest, TravelResult

if TYPE_CHECKING:
    from abacura_kallisti.atlas.room import Room


class TravelHelper(LOKPlugin):
    """Provides #go and #path commands"""

    def __init__(self) -> None:
        super().__init__()

    @command
    def path(self, destination: Room, detailed: bool = False) -> None:
        """
        Compute path to a room/location

        :param destination:  vnum or location name of travel destination
        :param detailed: display steps in a table with more information
        """

        nav = TravelGuide(self.world, self.pc, level=self.msdp.level, avoid_home=False)
        start = time.monotonic()
        nav_path = nav.get_path_to_room(self.msdp.room_vnum, destination.vnum, avoid_vnums=set())
        path_elapsed_time = time.monotonic() - start
        if not nav_path.destination:
            self.session.show_error(f"Unable to compute path to {destination.vnum}")
            return

        speedwalk = nav_path.get_simplified_path()

        title = f"Path to [ {destination.vnum } ] - {destination.name}"
        if not detailed:
            self.output(AbacuraPanel(f"{speedwalk}", title=title), highlight=True)
            return

        rows = []
        for step in nav_path.steps:
            if step.exit.to_vnum in self.world.rooms:
                terrain = self.world.rooms[step.exit.to_vnum].terrain_name
                # area = self.world.rooms[step.exit.to_vnum].area_name

                row = (
                    step.vnum,
                    step.exit.to_vnum,
                    step.exit.get_commands(),
                    step.exit.direction,
                    step.exit.door,
                    bool(step.exit.closes),
                    bool(step.exit.locks),
                    step.cost,
                    terrain,
                )
                rows.append(row)

        speedwalk = Text.assemble(("Speedwalk\n\n", OutputColors.section), (speedwalk, OutputColors.value))
        tbl = tabulate(
            rows,
            headers=("_Vnum", "_To Vnum", "Commands", "Direction", "Door", "Closes", "Locks", "Cost", "Terrain"),
            title="Steps",
            caption=f" Path computed in {1000 * path_elapsed_time:.1f}ms",
            show_footer=True,
        )

        tbl.columns[7].footer = str(nav_path.get_travel_cost())
        g = Group(speedwalk, Text(), tbl)
        self.output(AbacuraPanel(g, title=title), highlight=True)
        self.debuglog(f"#path metrics: {nav.metrics}")

    @command
    def go(self, destination: Room, avoid_home: bool = False) -> None:
        """
        Automatically go to a destination

        :param destination: A vnum or location name
        :param avoid_home: Do not use the 'home' command
        """

        def go_done(result: TravelResult) -> None:
            self.output(f"[bold purple] #go {result.result}", markup=True)

        tm = TravelRequest(destination=destination, avoid_home=avoid_home, callback_fn=go_done)
        self.dispatch(tm)

        # self.scripts.navigate(go_done, destination, avoid_home)
