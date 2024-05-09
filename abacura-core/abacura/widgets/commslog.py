"""A resizeable log window for communications"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import RichLog

from abacura.widgets.resizehandle import ResizeHandle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CommsLog(Container):
    """
    Textual container for scrolling, resizable widget.
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
        )
        self.tl = RichLog(id="commsTL", wrap=True, auto_scroll=True, max_lines=2000)
        self.tl.can_focus = False

    def compose(self) -> ComposeResult:
        yield self.tl
        yield ResizeHandle(self, "bottom")
