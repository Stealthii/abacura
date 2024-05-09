"""Debug console widget"""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

from abacura.widgets.resizehandle import ResizeHandle


class DebugDock(Widget):
    """Experimental debug window"""

    def __init__(self, id: str, name: str = "") -> None:
        super().__init__(id=id, name=name)
        self.tl = RichLog(id="debug", max_lines=2000, wrap=True)
        self.tl.can_focus = False

    def compose(self) -> ComposeResult:
        yield ResizeHandle(self, "top")
        yield self.tl
