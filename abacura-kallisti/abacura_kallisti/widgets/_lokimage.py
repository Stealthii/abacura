"""
Experimental pixel image widget

This depends on the vertical resolution doubling patch to rich-pixels
"""

from rich.console import RenderableType
from rich_pixels import Pixels
from textual.widgets import Static


class LOKImage(Static):
    img = None

    def show_image(self, height: int = 0, width: int = 0, image: str = "ship") -> None:
        if not height or not width:
            return
        self.img = Pixels.from_image_path("/home/tom/Pictures/Selection_986.jpg", resize=(width, height * 2))

    def render(self) -> RenderableType:
        return self.img or ""
