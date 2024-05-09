from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import plotext as plt
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class Plot(Static):
    def __init__(self, x: ArrayLike, y: ArrayLike, title: str = "", id: str | None = None) -> None:
        super().__init__(id=id)
        self.x = x
        self.y = y
        self.title = title

    def on_show(self) -> None:
        self.render_plot()

    def on_resize(self) -> None:
        self.render_plot()

    def render_plot(self) -> None:
        plt.clf()
        plt.plotsize(self.size.width, self.size.height)
        plt.plot(self.x, self.y)
        plt.title(self.title)
        plt.theme("pro")
        self.update(Text.from_ansi(plt.build()))

    def set_data(self, x: ArrayLike, y: ArrayLike) -> None:
        self.x = x
        self.y = y
        self.render_plot()


class PlotApp(App):
    CSS = """
        Plot {
            width: 100%;
            height: 1fr;
            margin: 1 2;
        }
    """

    def compose(self) -> ComposeResult:
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)

        with Vertical():
            yield Plot(x, y, id="plot")
            with Center():
                yield Button("Shift data", id="shift", variant="primary")

    @on(Button.Pressed, "#shift")
    def shift_data(self, event: Button.Pressed) -> None:
        rng = np.random.default_rng()
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x + rng.uniform(0, np.pi))
        self.query_one("#plot").set_data(x, y)


if __name__ == "__main__":
    app = PlotApp()
    app.run()
