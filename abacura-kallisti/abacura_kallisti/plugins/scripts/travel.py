from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from abacura.plugins import action
from abacura.plugins.events import AbacuraMessage, event
from abacura_kallisti.atlas.travel_guide import TravelGuide, TravelPath
from abacura_kallisti.plugins import LOKPlugin

if TYPE_CHECKING:
    from collections.abc import Callable

    from abacura_kallisti.atlas.room import Room, RoomMessage


@dataclass
class TravelRequest(AbacuraMessage):
    destination: Room | None = None
    avoid_home: bool = False
    callback_fn: Callable | None = None
    event_type: str = "lok.travel.request"


@dataclass
class TravelStatus(AbacuraMessage):
    destination: Room | None = None
    steps_remaining: int = 0
    event_type: str = "lok.travel.status"


@dataclass
class TravelResult(AbacuraMessage):
    success: bool = True
    result: str = ""
    event_type: str = "lok.travel.result"


class TravelScript(LOKPlugin):
    """Sends navigation commands after receiving lok.travel.request event"""

    def __init__(self) -> None:
        super().__init__()
        self.navigation_path: TravelPath | None = None
        self.travel_guide: TravelGuide | None = None
        self.retries = 0
        self.callback_fn: Callable | None = None

    @event(trigger="lok.travel.request")
    def handle_travel(self, message: TravelRequest) -> None:
        self.callback_fn = message.callback_fn
        self.start_nav(message.destination, message.avoid_home)
        self.retries = 0

    @event(trigger="lok.room")
    def got_room(self, _message: RoomMessage) -> None:
        # self.session.output(f"room event {_message.vnum} {_message.room.header}")
        if self.navigation_path:
            self.continue_nav()

    # wait 3 seconds and look again
    #    BLOCKING_GUARD = r"^(.*) blocks you from entering the city"

    @action(r"^Your mount is too exhausted.")
    def mount_exhausted(self) -> None:
        if self.navigation_path:
            self.cq.add(cmd="look", dur=0.1, delay=0, q="Move")

    @action(r"^Alas, you cannot go (.*)")
    def cannot_go(self) -> None:
        self.look_and_retry()

    @action(r"^You try to climb but couldn't get a good grip that time.")
    def cannot_climb(self) -> None:
        self.look_and_retry()

    @action(r"^(.*) is blocking your way")
    def blocking_way(self) -> None:
        self.look_and_retry()

    @action(r"^There's not enough room to fit in there!")
    def no_room(self) -> None:
        self.look_and_retry()

    def start_nav(self, destination: Room, avoid_home: bool = False) -> None:
        self.output(f"> start_nav {destination.vnum}")
        self.travel_guide = TravelGuide(self.world, self.pc, self.msdp.level, avoid_home)
        nav_path = self.travel_guide.get_path_to_room(self.msdp.room_vnum, destination.vnum, avoid_vnums=set())
        if not nav_path.destination:
            self.end_nav(False, f"Unable to compute path to {destination.vnum}")
            return

        self.dispatch(TravelStatus(destination=destination, steps_remaining=len(nav_path.steps)))
        self.navigation_path = nav_path
        self.cq.add(cmd="look", dur=0.1, delay=0, q="Move")

    def end_nav(self, success: bool, message: str) -> None:
        self.output(f"> end_nav: {success} {message}")
        self.travel_guide = None
        self.navigation_path = None
        self.dispatch(TravelStatus("lok.travel.status", steps_remaining=0))
        if self.callback_fn:
            self.callback_fn(TravelResult(success=success, result=message))

    def continue_nav(self) -> None:
        if self.msdp.room_vnum == self.navigation_path.destination.vnum:
            self.end_nav(True, "Arrived!")
            return

        room = self.world.rooms.get(self.msdp.room_vnum, None)
        if not room:
            self.end_nav(False, f"unknown room {self.msdp.room_vnum}, navigation halted")
            return

        if not self.navigation_path.truncate_remaining_path(self.msdp.room_vnum):
            self.output("LOST PATH")
            self.start_nav(self.navigation_path.destination)
            return

        self.retries = 0

        # TODO: Move logic into navigation path to get next command, handle portals
        for step in self.navigation_path.steps:
            if step.vnum != self.msdp.room_vnum:
                continue

            for cmd in step.exit.get_commands():
                if cmd.startswith("open") and self.msdp.room_exits.get(step.exit.direction) not in ("C", ""):
                    continue

                self.cq.add(cmd, dur=0, q="Move")

        self.dispatch(
            TravelStatus(destination=self.navigation_path.destination, steps_remaining=len(self.navigation_path.steps)),
        )

    def look_and_retry(self) -> None:
        if self.navigation_path:
            self.retries += 1
            if self.retries > 3:
                self.output(f"Navigation failed after {self.retries} tries")

            wait = 3
            if self.retries == 2:
                self.cq.add("breakout", dur=3, q="Priority")
                wait = 6

            self.cq.add("look", dur=0.1, delay=wait, q="Move")
