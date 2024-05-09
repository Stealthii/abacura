"""Legends of Kallisti Left Side Panel Dock"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from abacura.widgets.resizehandle import ResizeHandle
from abacura.widgets.sidebar import Sidebar

from ._lokaffects import LOKAffects
from ._lokcharacter import LOKCharacter
from ._lokexperience import LOKExperience
from ._lokodometer import LOKOdometer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class LOKLeft(Sidebar):
    """Left hand dock, intended for user widgets"""

    def compose(self) -> ComposeResult:
        yield ResizeHandle(self, "right")
        with Container(id="leftsidecontainer", classes="SidebarContainer"):
            yield LOKCharacter(id="lok_character")
            yield LOKAffects(id="lok_affects")
            yield LOKExperience(id="lok_experience")
            yield LOKOdometer(id="lok_odometer")
