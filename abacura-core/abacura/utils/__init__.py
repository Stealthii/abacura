from __future__ import annotations

import re
from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numbers import Real

_pct_colors = OrderedDict()
_pct_colors[80] = "green"
_pct_colors[60] = "green_yellow"
_pct_colors[40] = "yellow"
_pct_colors[20] = "dark_orange3"
_pct_colors[0] = "red"

ansi_escape = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def percent_color(cval: Real) -> str:
    for key, value in _pct_colors.items():
        if key < cval:
            return value
    return "dark_red"


def human_format(num: str | float) -> str:
    if isinstance(num, str):
        num = int(num)
    num = float(f"{num:.3g}")
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(f"{num:f}".rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude])
