from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Input

from abacura.plugins import Plugin, command
from abacura.screens import AbacuraWindow
from abacura_kallisti.widgets import LOKMap


class BigMapWindow(AbacuraWindow):
    """Log Screen with a search box"""

    BINDINGS = [
        ("pageup", "pageup", "PageUp"),
        ("pagedown", "pagedown", "PageDown"),
        ("shift+end", "scroll_end", ""),
        ("shift+home", "scroll_home", ""),
    ]

    CSS_PATH = "css/kallisti.css"

    def __init__(self) -> None:
        super().__init__(title="Big Map")
        self.input = Input(id="logsearch-input", placeholder="search text")
        self.bigmap: LOKMap = LOKMap(id="bigmap", resizer=False)

    def compose(self) -> ComposeResult:
        with Grid(id="bigmap-grid"):
            yield self.bigmap

    def remove(self) -> None:
        self.bigmap.unregister()
        super().remove()


class BigMap(Plugin):
    @command
    def map(self) -> None:
        """
        Show a big map window
        """

        window = BigMapWindow()
        self.session.screen.mount(window)
        return
