from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual.widget import Widget
from textual.widgets import ProgressBar, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.timer import Timer


class IndeterminateProgressBar(Widget):
    progress_timer: Timer
    """Timer to simulate progress happening."""

    def compose(self) -> ComposeResult:
        yield Static("Remort Progress", classes="WidgetTitle")
        yield ProgressBar(show_eta=True, show_percentage=True)

    def on_mount(self) -> None:
        """Set up a timer to simulate progess happening."""
        self.progress_timer = self.set_interval(1, self.make_progress, pause=True)
        self.action_start()

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        pb = self.query_one(ProgressBar)
        pb.progress = random.randint(1, 99)
        if pb.percentage == 100:
            pb.update(total=pb.total + pb.total)
            pb.progress = 0

    def action_start(self) -> None:
        """Start the progress tracking."""
        self.query_one(ProgressBar).update(total=100)
        self.progress_timer.resume()
