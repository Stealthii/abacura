"""
Menu bar widget

Intended for top of screen but you do you
"""

from typing import Callable

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.events import Click
from textual.widgets import Input, OptionList, Static


class SubMenu(OptionList):
    """A submenu"""

    COMPONENT_CLASSES = {
        "submenu--selected-item",
    }
    DEFAULT_CSS = """
        SubMenu option-list--option {
            padding: 0 0;
        }
    """
    BINDINGS = [("escape", "remove", "close menu")]

    def __init__(self, *, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self._options_callable: dict[str, Callable] = {}

    def action_remove(self) -> None:
        self.remove()

    def on_option_list_option_selected(self, evt: OptionList.OptionMessage) -> None:
        evt.stop()
        self.remove()
        self._options_callable[str(evt.option.prompt)]()

    def add_options(self, items: dict[str, Callable]) -> None:
        super().add_options(items)
        self._options_callable.update(items)


class MenuItem(Static):
    DEFAULT_CSS = """
    MenuItem {
        width: auto;
        padding: 0 1;
    }
    """

    def __init__(self, renderable: RenderableType = "") -> None:
        super().__init__(renderable)
        self._submenu_items: dict[str, Callable] = {}

    def add_submenu_item(self, label: str, callback: Callable) -> None:
        """Add a submenu item"""
        self._submenu_items[label] = callback

    def on_click(self, evt: Click) -> None:
        try:
            sub = self.screen.query_one("#submenu")
            sub.remove()
        except NoMatches:
            pass

        sub_menu = SubMenu(classes="popover", id="submenu")
        sub_menu.add_options(self._submenu_items)
        sub_menu.styles.offset = (self.content_region.x, evt.screen_y + 1)
        sub_menu.styles.width = 15
        self.screen.mount(sub_menu)
        sub_menu.focus()


class MenuBar(Static):
    """Menu widget, with drop downs and selections"""

    DEFAULT_CSS = """
        MenuBar {
            height: 1;
            dock: top;
            background: $primary-background;
            layers: below above;
        }
        .popover {
            layer: above;
        }
    """

    def __init__(self) -> None:
        super().__init__()
        self._menu_items: list[MenuItem] = []

    def compose(self) -> ComposeResult:
        with Horizontal():
            for m_item in self._menu_items:
                yield m_item

    def add_menu_item(self, menu_item: MenuItem) -> None:
        """Add an item to the menu"""
        self._menu_items.append(menu_item)


class MenuApp(App):
    """A simple app to show our widget."""

    DEFAULT_CSS = """
        #SampleBlock {
            height: 13;
            width: 100%;
        }

    """
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.bar = MenuBar()
        menu_item = MenuItem("Freaky")
        menu_item.add_submenu_item("Test", self.test_called)
        menu_item.add_submenu_item("Best", self.best_called)
        self.bar.add_menu_item(menu_item)
        menu_item = MenuItem("Noise")
        menu_item.add_submenu_item("Woop", self.woop_called)
        menu_item.add_submenu_item("Womp", self.womp_called)
        self.bar.add_menu_item(menu_item)
        self.static = Static(id="SampleBlock")

    def compose(self) -> ComposeResult:
        yield self.bar
        yield self.static
        yield Input()

    def test_called(self) -> None:
        self.static.update("You clicked test")

    def best_called(self) -> None:
        self.static.update("You clicked best")

    def woop_called(self) -> None:
        self.static.update("You clicked woop")

    def womp_called(self) -> None:
        self.static.update("You clicked wonp")


if __name__ == "__main__":
    app = MenuApp()
    app.run()
