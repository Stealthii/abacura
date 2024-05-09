from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import astuple, dataclass, fields, is_dataclass
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

from rich import box as rich_box
from rich.console import Group, JustifyMethod, RenderableType
from rich.panel import Panel
from rich.style import Style, StyleType
from rich.table import Table
from rich.text import Text, TextType

if TYPE_CHECKING:
    from rich.align import AlignMethod
    from rich.padding import PaddingDimensions


@dataclass
class OutputColors:
    output: str = "#101018"
    panel: str = "#334455"  # Charcoal
    border: str = "#DDEEFF"
    section: str = "#11EEFF"  # Cyan
    title: str = section
    field: str = "#FFFFFF"
    value: str = "#DDDDDD"
    caption: str = "gray50"
    success: str = "#11FF22"  # green
    exception: str = "#FF1133"  # Red
    error: str = "#FF7711"  # Orange
    warning: str = "#FFDD55"  # Yellow


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


class AbacuraTable(Table):
    def __init__(
        self,
        title: TextType | None = None,
        caption: TextType | None = None,
        box: rich_box.Box | None = rich_box.HORIZONTALS,
        expand: bool = False,
        show_footer: bool = False,
        style: StyleType = OutputColors.value,
        header_style: StyleType | None = Style(color=OutputColors.field, bold=True),
        footer_style: StyleType | None = Style(color=OutputColors.field, bold=True),
        border_style: StyleType | None = OutputColors.border,
        title_style: StyleType | None = Style(color=OutputColors.title),
        caption_style: StyleType | None = OutputColors.caption,
        title_justify: JustifyMethod = "left",
        caption_justify: JustifyMethod = "left",
    ) -> None:
        super().__init__(
            title=title,
            caption=caption,
            box=box,
            expand=expand,
            show_footer=show_footer,
            style=style,
            header_style=header_style,
            footer_style=footer_style,
            border_style=border_style,
            title_style=title_style,
            caption_style=caption_style,
            title_justify=title_justify,
            caption_justify=caption_justify,
        )


class AbacuraPropertyGroup(Group):
    def __init__(
        self,
        obj: dict | IsDataclass,
        title: str = "Properties",
        exclude: set | None = None,
    ) -> None:
        if not isinstance(obj, dict):
            obj = {f.name: getattr(obj, f.name) for f in fields(obj)}

        kl = max([len(k) for k in obj.keys()])
        lines = [Text.assemble((title, OutputColors.section), ("\n", ""))]
        for k, v in obj.items():
            if exclude and k in exclude:
                continue
            text = Text.assemble(
                (f"{k:>{kl}.{kl}}: ", Style(color=OutputColors.field, bold=True)),
                (str(v), OutputColors.value),
            )
            lines.append(text)

        super().__init__(*lines)


class AbacuraPanel(Panel):
    def __init__(
        self,
        renderable: RenderableType,
        box: rich_box.Box = rich_box.ROUNDED,
        *,
        title: TextType = "",
        title_align: AlignMethod = "left",
        expand: bool = False,
        style: StyleType = Style(bgcolor=OutputColors.panel),
        border_style: StyleType = Style(bold=True, bgcolor=OutputColors.panel),
        padding: PaddingDimensions = 1,
        highlight: bool = True,
    ) -> None:
        p = Panel(
            renderable=renderable,
            box=box,
            title=title,
            title_align=title_align,
            expand=expand,
            style=style,
            border_style=border_style,
            padding=padding,
            highlight=highlight,
        )
        super().__init__(p, box=rich_box.SIMPLE, padding=1, expand=False)


class AbacuraWarning(AbacuraPanel):
    def __init__(
        self,
        renderable: RenderableType,
        box: rich_box.Box = rich_box.SQUARE,
        *,
        title: TextType,
        border_style: StyleType = Style(color=OutputColors.warning, bold=True),
    ) -> None:
        super().__init__(
            renderable=renderable,
            box=box,
            title=title,
            border_style=border_style,
        )


class AbacuraError(AbacuraPanel):
    def __init__(
        self,
        renderable: RenderableType,
        box: rich_box.Box = rich_box.SQUARE,
        *,
        title: TextType,
        border_style: StyleType = Style(color=OutputColors.error, bold=True),
    ) -> None:
        super().__init__(
            renderable=renderable,
            box=box,
            title=title,
            border_style=border_style,
        )


def tabulate(
    tabular_data: list[dict] | list[IsDataclass] | list[tuple] | list[str],
    headers: list[str] | str | None = None,
    float_format: str = "9.3f",
    row_styler: Callable[[str | dict | IsDataclass | Iterable], str] | None = None,
    *,
    title: TextType | None = None,
    caption: TextType | None = None,
    box: rich_box.Box | None = rich_box.HORIZONTALS,
    expand: bool = False,
    show_footer: bool = False,
    header_style: StyleType | None = Style(color=OutputColors.field, bold=True),
) -> AbacuraTable:
    """
    Create a rich Table with automatic justification for numbers and a configurable floating point format.

    tabular_data can be a List[List], List[Dict], List[Tuple], List[dataclass], List[str]
    headers should be an interable list/tuple of header names
    kwargs are passed through to rich Table

    """
    # title="", title_justify="left", title_style=None,
    # caption="", caption_justify="left", caption_style=None,
    # header_style=None, border_style=None,

    tbl = AbacuraTable(
        title=title,
        caption=caption,
        box=box,
        expand=expand,
        show_footer=show_footer,
        header_style=header_style,
    )

    if isinstance(headers, str):
        headers = [headers]
    elif headers is None:
        headers = []

    if len(tabular_data) == 0:
        if len(headers) == 0:
            return tbl
        column_types = [str for _ in headers]
    elif isinstance(tabular_data[0], dict):
        keys = tabular_data[0].keys()
        headers = headers if len(headers) else list(keys)
        tabular_data = [[row.get(k, None) for k in keys] for row in tabular_data]
        column_types = [type(v) for v in tabular_data[0]]
    elif is_dataclass(tabular_data[0]):
        df = fields(tabular_data[0])
        headers = headers if len(headers) else list([f.name for f in df])
        tabular_data = [astuple(row) for row in tabular_data]
        column_types = [f.type for f in df]
    elif not isinstance(tabular_data[0], Iterable) or isinstance(tabular_data[0], str):
        tabular_data = [[row] for row in tabular_data]
        column_types = [type(v) for v in tabular_data[0]]
    else:
        column_types = [type(v) for v in tabular_data[0]]

    row_styles = [""] * len(tabular_data)
    if row_styler:
        row_styles = [row_styler(row) for row in tabular_data]

    for h, ct in zip_longest(headers, column_types):
        if h and h.startswith("_"):
            justify = "right"
        elif ct in (int, "int", float, "float"):
            justify = "right"
        else:
            justify = "left"
        hdr = h.lstrip("_") if h else ""
        tbl.add_column(header=hdr, justify=justify)

    for i, row in enumerate(tabular_data):
        values = [format(v, float_format) if ct in (float, "float") else str(v) for ct, v in zip(column_types, row)]
        tbl.add_row(*values, style=row_styles[i])

    return tbl
