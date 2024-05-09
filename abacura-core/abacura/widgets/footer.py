"""
Various footer widget bits
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widgets import Footer

from abacura.plugins.events import event

if TYPE_CHECKING:
    from abacura.mud.options.msdp import MSDPMessage


# TODO this should probably be a specific implementation in abacura-kallisti
class AbacuraFooter(Footer):
    """Bottom of screen bar with current session name"""

    def __init__(self, id: str = "") -> None:
        super().__init__()
        self.id = id

    session_name: reactive[str | None] = reactive[str | None]("null")
    level: reactive[str] = reactive[str]("")

    def on_mount(self) -> None:
        self.screen.session.add_listener(self.update_level)

    def render(self) -> str:
        return f"#{self.session_name} {self.level}"

    @event("core.msdp.LEVEL", priority=5)
    def update_level(self, message: MSDPMessage) -> None:
        """Update reactive values for level"""

        self.level = f"Level: {message.value}"
