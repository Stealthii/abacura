from __future__ import annotations

import time
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self


class TimerError(Exception):
    """A cus
    tom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """Time your code using a class, context manager, or decorator"""

    timers: ClassVar[dict[str, float]] = {}
    name: str | None = None
    text: str = "{:s}: {:0.6f} seconds"
    logger: Callable[[str], None] | None = print
    _start_time: float | None = field(default=None, init=False, repr=False)

    def __init__(self, name: str = "Elapsed") -> None:
        self.name = name
        super().__init__()

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            self.logger(self.text.format(self.name, elapsed_time))

        if self.name:
            self.timers[self.name] = self.timers.get(self.name, 0) + elapsed_time

        return elapsed_time

    def __enter__(self) -> Self:
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Stop the context manager timer"""
        self.stop()
