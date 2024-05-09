from __future__ import annotations

from abacura.plugins import Plugin, command
from abacura.utils.pycharm import PycharmDebugger


class PycharmDebug(Plugin):
    """Connect to the remote pycharm debugger"""

    def __init__(self) -> None:
        super().__init__()
        self.debugger: PycharmDebugger | None = None

    @command(hide=True)
    def pycharm_debug(self, host: str = "localhost", port: int = 12345) -> None:
        """
        Connect to the remote pycharm debugger

        :param host: Host running pycharm debugger
        :param port: port of the debugger
        """
        self.debugger = PycharmDebugger()
        try:
            self.output(f"Connecting to {host}:{port}")
            self.debugger.connect(host, port)
        except ConnectionRefusedError:
            self.output(f"Connection refused by pycharm debugger {host}:{port}")
