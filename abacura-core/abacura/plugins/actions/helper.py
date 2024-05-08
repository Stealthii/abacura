from __future__ import annotations

from abacura.plugins import Plugin, command
from abacura.utils.renderables import AbacuraPanel, tabulate


class ActionCommand(Plugin):
    """Provides #ticker command"""

    def show_actions(self) -> None:
        rows = []
        for action in self.director.action_manager.actions.queue:
            callback_name = getattr(action.callback, "__qualname__", str(action.callback))
            # source = action.source.__class__.__name__ if action.source else ""

            rows.append((repr(action.pattern), callback_name, action.priority, action.flags))

        tbl = tabulate(
            rows,
            headers=["Pattern", "Callback", "Priority", "Flags"],
            caption=f" {len(rows)} actions registered",
        )
        self.output(AbacuraPanel(tbl, title="Registered Actions"))

    @command
    def action(self) -> None:
        """
        View actions

        """
        self.show_actions()
