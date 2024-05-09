"""Debug console widget"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widget import Widget
from textual.widgets import RichLog

from abacura.widgets.resizehandle import ResizeHandle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class DebugDock(Widget):
    """Experimental debug window"""

    def __init__(self, id: str, name: str = "") -> None:
        super().__init__(id=id, name=name)
        self.tl = RichLog(id="debug", max_lines=2000, wrap=True)
        self.tl.can_focus = False

    def compose(self) -> ComposeResult:
        yield ResizeHandle(self, "top")
        yield self.tl
