from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Static

from abacura.widgets.resizehandle import ResizeHandle

if TYPE_CHECKING:
    from textual.app import ComposeResult

SIDEBAR_CONTENT = """
Character: Kensho
Mugwump delta four

Stats go here

Affects go here

"""


class Sidebar(Container):
    """Generic Sidebar"""

    def compose(self) -> ComposeResult:
        """Composes the subwidgets of a sidebar"""
        yield Static(SIDEBAR_CONTENT)
        yield ResizeHandle(self, "right")
