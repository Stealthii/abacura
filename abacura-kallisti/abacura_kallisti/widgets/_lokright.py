"""Legends of Kallisti Right Side Panel Dock"""

from textual.app import ComposeResult
from textual.containers import Container

from abacura.widgets.resizehandle import ResizeHandle
from abacura.widgets.sidebar import Sidebar
from abacura_kallisti.widgets import LOKCombat, LOKGroup, LOKMap, LOKTaskQueue, LOKZone


class LOKRight(Sidebar):
    """Right hand dock, intended for user widgets"""

    def compose(self) -> ComposeResult:
        yield ResizeHandle(self, "left")
        with Container(id="rightsidecontainer", classes="SidebarContainer"):
            yield LOKMap(id="lokmap")
            yield LOKZone(id="lokzone")
            yield LOKGroup(id="lokgroup")
            yield LOKCombat(id="lokcombat")
            yield LOKTaskQueue(id="loktaskqueue")
