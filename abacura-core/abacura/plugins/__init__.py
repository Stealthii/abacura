from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from abacura.plugins.actions import Action
from abacura.plugins.commands import CommandArgumentError, CommandError
from abacura.plugins.tickers import Ticker

if TYPE_CHECKING:
    from typing import Any, TypeVar

    from abacura.config import Config
    from abacura.mud import OutputMessage
    from abacura.mud.options.msdp import MSDP
    from abacura.mud.session import Session
    from abacura.plugins.director import Director
    from abacura.plugins.task_queue import TaskManager
    from abacura.utils.fifo_buffer import FIFOBuffer

    T = TypeVar("T", bound=Callable[..., Any])


class ContextProvider:
    def __init__(self, config: Config, session_name: str) -> None:
        pass

    def get_injections(self) -> dict:
        return {}


class Plugin:
    """Generic Plugin Class"""

    _context: dict = {}

    def __init__(self) -> None:
        # super().__init__()
        self._source_filename: str = ""
        self.session: Session = self._context["session"]
        self.config: Config = self._context["config"]
        self.director: Director = self._context["director"]
        self.core_msdp: MSDP = self._context["core_msdp"]
        self.cq: TaskManager = self._context["cq"]
        self.output_history: FIFOBuffer[OutputMessage] = self._context["buffer"]
        self.output = self.session.output
        self.debuglog = self.session.debuglog
        self.dispatch = self.director.event_manager.dispatch
        self.register_actions = True

    @classmethod
    def set_context(cls, context: dict) -> None:
        cls._context = context

    def get_name(self) -> str:
        return self.__class__.__name__

    def get_help(self) -> Any:
        doc = getattr(self, "__doc__", None)
        return doc

    def add_action(self, pattern: str, callback_fn: Callable, flags: int = 0, name: str = "", color: bool = False) -> None:
        act = Action(source=self, pattern=pattern, callback=callback_fn, flags=flags, name=name, color=color)
        self.director.action_manager.add(act)

    def remove_action(self, name: str) -> None:
        self.director.action_manager.remove(name)

    def add_ticker(self, seconds: float, callback_fn: Callable, repeats: int = -1, name: str = "", commands: str = "") -> None:
        t = Ticker(source=self, seconds=seconds, callback=callback_fn, repeats=repeats, name=name, commands=commands)
        self.director.ticker_manager.add(t)

    def remove_ticker(self, name: str) -> None:
        self.director.ticker_manager.remove(name)

    def add_substitute(self, pattern: str, repl: str, name: str = "") -> None:
        pass

    def remove_substitute(self, name: str) -> None:
        pass

    def send(self, message: str, raw: bool = False, echo_color: str = "orange1") -> None:
        self.session.send(message, raw=raw, echo_color=echo_color)


def action(pattern: str, flags: int = 0, color: bool = False, priority: int = 0) -> Callable[[T], T]:
    def add_action(action_fn: T) -> T:
        setattr(action_fn, "action_pattern", pattern)
        setattr(action_fn, "action_color", color)
        setattr(action_fn, "action_flags", flags)
        setattr(action_fn, "action_priority", priority)
        return action_fn

    return add_action


def command(function: T | None = None, name: str = "", hide: bool = False, override: bool = False) -> Callable[[T], T]:
    def add_command(fn: T) -> T:
        setattr(fn, "command_name", name or fn.__name__)
        setattr(fn, "command_hide", hide)
        setattr(fn, "command_override", override)
        return fn

    if function:
        return add_command(function)

    return add_command


def ticker(seconds: float, repeats: int = -1, name: str = "") -> Callable[[T], T]:
    def add_ticker(fn: T) -> T:
        setattr(fn, "ticker_seconds", seconds)
        setattr(fn, "ticker_repeats", repeats)
        setattr(fn, "ticker_name", name)
        return fn

    return add_ticker


__all__ = [
    "CommandArgumentError",
    "CommandError",
    "ContextProvider",
    "Plugin",
    "action",
    "command",
    "ticker",
]
