"""Legends of Kallisti Right Side Panel Dock"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from abacura.widgets.resizehandle import ResizeHandle
from abacura.widgets.sidebar import Sidebar

from ._lokcombat import LOKCombat
from ._lokgroup import LOKGroup
from ._lokmap import LOKMap
from ._loktask_queue import LOKTaskQueue
from ._lokzone import LOKZone

if TYPE_CHECKING:
    from textual.app import ComposeResult


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
