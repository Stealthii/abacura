"""
The mud module contains Session objects and protocol handlers
"""

import re
import traceback

from rich.traceback import Traceback

from abacura.utils.renderables import AbacuraError, AbacuraWarning, Panel, box

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class OutputMessage:
    def __init__(self, message: str, gag: bool = False) -> None:
        self.message: str = message
        if isinstance(message, str):
            self.stripped = ansi_escape.sub("", message)
        else:
            self.stripped = message
        self.gag: bool = gag


class BaseSession:
    """Base class for all Session objects"""

    def output(self, msg, **kwargs) -> None:
        """Subclasses will handle this"""

    def debuglog(self, msg, **kwargs) -> None:
        """Subclasses will handle this"""

    def outputlog(self, message: OutputMessage) -> None:
        """Subclasses will handle this"""

    def show_warning(self, msg, title: str = "Warning") -> None:
        self.output(AbacuraWarning(msg, title=title), markup=True, highlight=True)

    def show_error(self, msg, title: str = "Error") -> None:
        self.output(AbacuraError(msg, title=title), markup=True, highlight=True)

    def show_exception(self, exc: Exception, msg: str = "", show_tb: bool = True, to_debuglog: bool = False) -> None:
        """Show an exception with optional traceback"""

        self.outputlog(OutputMessage(msg))
        self.outputlog(OutputMessage("".join(traceback.format_exception(type(exc), exc, exc.__traceback__))))

        if show_tb:
            t = Traceback.from_exception(type(exc), exc, exc.__traceback__, show_locals=False)
            p = Panel(t, box=box.SIMPLE, expand=False)
            if to_debuglog:
                self.debuglog(p, facility="error")
            else:
                self.output(p)
        else:
            msg = repr(exc) if msg == "" else msg
            self.show_error(msg)
            # self.output(AbacuraError(msg, title="Exception"), markup=True, highlight=True)
